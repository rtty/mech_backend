import math
import os
import re

import xlrd
from django.db import transaction
from django.db.models import CharField
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.db.utils import IntegrityError

from app.exceptions.http import HttpException
from app.models import (Project, ProjectsHasVin, SubVin, Test, TestCategory,
                        Vin, VinTests)
from app.parser import constants

from .async_task import AsyncTaskService
from .rule import RuleService
from .rule_version import RuleVersionService


class FileImportService:
    """
    file import service

    import_project(): create projects, vins and subvins from an Excel file
    import_rule(): create a rule, rule version and mappings from an Excel file
    """

    def __init__(self):
        """
        init parser and constants
        """
        constants.read_parser_out_file()

    def import_project(self, file, task_id):
        task = AsyncTaskService().get_async_task(task_id)

        try:
            sheet = xlrd.open_workbook(file_contents=file.read()).sheet_by_index(0)
            projects = self.__fill_to(self.__get_column(sheet, 0), sheet.nrows - 1)
            vins = self.__fill_to(self.__get_column(sheet, 1), sheet.nrows - 1)
            subvins = self.__fill_to(self.__get_column(sheet, 2), sheet.nrows - 1)
        except Exception as e:
            task.finish_with_error(str(e))
            raise HttpException(400, 'Invalid Excel file')

        try:
            pattern = re.compile('(?P<name>.+?)(?P<q>\*qualifier\w*)?$', re.IGNORECASE)
            # We're creating a dictionary which for each Test has a list of values corresponding with sheet's rows and another similar one for qualifiers
            tests = {}
            qualifiers = {}
            for i in range(3, sheet.ncols):
                test_data = pattern.match(sheet.cell(0, i).value).groupdict()
                test = Test.objects.get(name=test_data['name'])
                if test_data['q'] is None:
                    tests[test] = [
                        x.strip() if x.strip() != '' else None for x in self.__get_column(sheet, i)
                    ]
                else:
                    qualifiers[test] = [
                        x.strip() if x.strip() != '' else None for x in self.__get_column(sheet, i)
                    ]
        except AttributeError as err:
            task.finish_with_error(str(err))
            raise HttpException(400, 'Invalid Excel file: wrong format: ' + str(err))
        except Test.DoesNotExist as err:
            task.finish_with_error(str(err))
            raise HttpException(400, 'Invalid Excel file: wrong test name or type')
        except ValueError as err:
            task.finish_with_error(str(err))
            raise HttpException(400, 'Invalid Excel file: test value must be float')

        try:
            Project.objects.bulk_create((Project(name=i) for i in projects), ignore_conflicts=True)
            projects_dict = Project.objects.filter(name__in=projects).in_bulk(field_name='name')

            Vin.objects.bulk_create((Vin(name=i) for i in vins), ignore_conflicts=True)
            vins_dict = Vin.objects.filter(name__in=vins).in_bulk(field_name='name')

            project_id = None
            vin_id = None
            project_vin = []
            result = []
            cancelled = False

            subvins_set = set()
            subvins_data = {}
            data_set = set()
            data = {}
            data_q_set = set()
            data_q = {}

            for index in range(sheet.nrows - 1):
                print(index)
                if projects[index]:
                    project_id = projects_dict[projects[index]].pk
                    result.append(project_id)
                if project_id is None:
                    task.finish_with_error('No project in row {}'.format(index + 2))
                    return
                if vins[index]:
                    vin_id = vins_dict[vins[index]].pk
                    project_vin.append((project_id, vin_id))
                if vin_id is None and subvins[index]:
                    return task.finish_with_error('No Vin in row {}'.format(index + 2))
                if subvins[index]:
                    subvins_set.add(subvins[index])
                    subvins_data[subvins[index]] = vin_id
                if vin_id is not None:
                    for test_id in tests.keys():
                        value = tests[test_id][index]
                        if value is not None:
                            key = '#'.join(str(x) for x in [project_id, vin_id, test_id])
                            data_set.add(key)
                            data[key] = value
                    for test, q_list in qualifiers.items():
                        value = tests[test][index]
                        qualifier = q_list[index]
                        if value is not None and qualifier is not None:
                            key = '#'.join(str(x) for x in [project_id, vin_id, test_id])
                            data_q_set.add(key)
                            data_q[key] = (value, qualifier)
                task.progress = math.floor(80 * (index + 1) / (sheet.nrows - 1))
                task.save(update_fields=['progress'])
                task.refresh_from_db()
                if not task.is_running:
                    cancelled = True
                    break

            if not cancelled:
                ProjectsHasVin.objects.bulk_create(
                    (ProjectsHasVin(project_id=t[0], vin_id=t[1]) for t in project_vin),
                    ignore_conflicts=True,
                )
                del project_vin

                existins_subvins = SubVin.objects.filter(name__in=subvins_set).in_bulk(
                    field_name='name'
                )
                subvins_to_create = subvins_set.difference(existins_subvins.keys())
                SubVin.objects.bulk_create(
                    (SubVin(name=name, vins_id=subvins_data[name]) for name in subvins_to_create),
                    ignore_conflicts=True,
                )

                for name, subvin in existins_subvins.items():
                    subvin.vins_id = subvins_data[name]
                SubVin.objects.bulk_update(existins_subvins, ['vins_id'])
                del existins_subvins
                del subvins_to_create

                v = V('#')

                # in_bulk doesn't work for annotated fields
                existing_vin_tests = {
                    vt.key: vt
                    for vt in VinTests.objects.filter(qualifier=None)
                    .annotate(
                        key=Concat(
                            'project_id',
                            V('#'),
                            'vin_id',
                            V('#'),
                            'tests_id',
                            output_field=CharField(),
                        )
                    )
                    .filter(key__in=data_set)
                }
                vin_tests_to_create = data_set.difference(existing_vin_tests.keys())
                VinTests.objects.bulk_create(
                    (
                        VinTests(**self.__key_to_attrs(key), value=data[key])
                        for key in vin_tests_to_create
                    ),
                    ignore_conflicts=True,
                )

                vt_to_update = {
                    k: vt for k, vt in existing_vin_tests.items() if data[k] != vt.value
                }
                for key, vin_test in existing_vin_tests.items():
                    vin_test.value = data[key]
                VinTests.objects.bulk_update(vt_to_update.values(), ['value'], batch_size=1000)

                del data
                del data_set

                task.progress = 90
                task.save(update_fields=['progress'])
                task.refresh_from_db()
                if not task.is_running:
                    return task

                # in_bulk doesn't work for annotated fields
                existing_vin_tests = {
                    vt.key: vt
                    for vt in VinTests.objects.filter(qualifier__isnull=False)
                    .annotate(
                        key=Concat(
                            'project_id',
                            v,
                            'vin_id',
                            v,
                            'tests_id',
                            output_field=CharField(),
                        )
                    )
                    .filter(key__in=data_q_set)
                }
                vin_tests_to_create = data_q_set.difference(existing_vin_tests.keys())
                VinTests.objects.bulk_create(
                    (
                        VinTests(
                            **self.__key_to_attrs(key),
                            value=data_q[key][0],
                            qualifier=data_q[key][1]
                        )
                        for key in vin_tests_to_create
                    ),
                    ignore_conflicts=True,
                )

                vt_to_update = {
                    k: vt
                    for k, vt in existing_vin_tests.items()
                    if data_q[k] != (vt.value, vt.qualifier)
                }
                for key, vin_test in vt_to_update.items():
                    vin_test.value, vin_test.qualifier = data_q[key]
                VinTests.objects.bulk_update(
                    vt_to_update.values(), ['value', 'qualifier'], batch_size=1000
                )
                task.progress = 100
                task.is_running = False
                task.result = result
                task.save()
                return task
        except Exception as e:
            task.finish_with_error(str(e))

    def import_rule(self, file, user_data):
        try:
            with transaction.atomic():
                rule, created = RuleService().create_new_rule(
                    dict(name=os.path.splitext(file.name)[0])
                )
                if not created:
                    return rule
                rule_version = RuleVersionService().create_new_rule_version(
                    rule.id,
                    user_data,
                    dict(versionNumber='v1.0', notes='Import from File'),
                )
                RuleVersionService().lock_unlock_rule_version(user_data, True, rule_version.id)
                try:
                    book = xlrd.open_workbook(file_contents=file.read())
                except:
                    raise HttpException(400, 'Invalid Excel file')
                text = '\n'.join(map(lambda x: x.value, book.sheet_by_name('Text').col(0)))
                RuleVersionService().convert_plain_text(
                    user_dict=user_data, data=dict(newText=text), id=rule_version.id
                )
                RuleVersionService().lock_unlock_rule_version(user_data, False, rule_version.id)
                rule_version.save()
                return RuleService().get_rule(rule.id)
        except IntegrityError as err:
            raise HttpException(400, 'Invalid Excel file: ' + str(err))

    def import_mappings(self, file, user_data):
        try:
            with transaction.atomic():
                try:
                    book = xlrd.open_workbook(file_contents=file.read())
                    mappings = book.sheet_by_name('Mappings')
                    categories = self.__get_column(mappings, 0)
                    tests = self.__get_column(mappings, 1)
                    categories = self.__fill_to(categories, len(tests))
                except:
                    raise HttpException(400, 'Invalid Excel file')
                category = None
                result_tests = []
                for index, test in enumerate(tests):
                    if categories[index]:
                        category, created = TestCategory.objects.get_or_create(
                            name=categories[index]
                        )
                    if category is None:
                        raise HttpException(400, 'No category for test "' + test + '"')
                    new_test, created = Test.objects.get_or_create(
                        name=test, defaults=dict(test_category=category)
                    )
                    result_tests.append(new_test)

                return result_tests
        except IntegrityError as err:
            raise HttpException(400, 'Invalid Excel file: ' + str(err))

    def __get_column(self, sheet, index):
        """
        Get a list of values from the given column in Excel `sheet`
        :param sheet: :class:`~xlrd.sheet.Sheet`
        :param index: index of the chosen column, zero-based
        :return: list of string values
        """
        if index >= sheet.ncols:
            return []
        return list(map(lambda x: str(x.value).strip(), sheet.col(index)))[1:]

    def __fill_to(self, l, length, value=''):
        """
        extends a list to `length` with `value`
        :param l: list
        :param length: length to which `l` should be extended
        :param value: value to fill new elements with
        :return: extended list
        """
        return l + [value] * (length - len(l))

    def __key_to_attrs(self, key: str):
        attrs = key.split('#')
        return {
            'project_id': int(attrs[0]),
            'vin_id': int(attrs[1]),
            'tests_id': int(attrs[3].split(':')[0]),
        }
