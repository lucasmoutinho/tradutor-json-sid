import pytest
from parameterized import parameterized

import json
import copy

from app.lib import sasdgfunc


import logging
logger = logging.getLogger('test')


class Test_sasdgfunc():
    # Data for bi-directional tests
    # Input and output of fromFlatJSON should be equal output and input of toFlatJSON respectively
    # It means that if output of fromFlatJSON will be given as input for toFlatJSON,
    # it produce the same result as input of fromFlatJSON. And vice versa
    def define_test_data():
        test_params = []

        # Empty datagrid
        fj = []
        dg = [{'metadata': []}, {'data': []}]
        test_params.append(['empty', copy.deepcopy(fj), copy.deepcopy(dg)])

        # Two columns, one row, all decimal (integers)
        fj = [{'a': 5, 'b': 7}]
        dg = [{'metadata': [{'a': 'decimal'}, {'b': 'decimal'}]}, {'data': [[5, 7]]}]
        test_params.append(['simple_decimal', copy.deepcopy(fj), copy.deepcopy(dg)])

        # Two columns, two rows, value with fraction
        fj = [{'a': 5, 'b': 7}, {'a': 10.3, 'b': 11}]
        dg = [{'metadata': [{'a': 'decimal'}, {'b': 'decimal'}]}, {'data': [[5, 7], [10.3, 11]]}]
        test_params.append(['decimal_2r', copy.deepcopy(fj), copy.deepcopy(dg)])

        # Null for decimal
        fj = [{'a': 5, 'b': 7}, {'a': 10.3, 'b': None}]
        dg = [{'metadata': [{'a': 'decimal'}, {'b': 'decimal'}]}, {'data': [[5.0, 7.0], [10.3, None]]}]
        test_params.append(['decimal_null', copy.deepcopy(fj), copy.deepcopy(dg)])

        # Simple string
        fj = [{'a': 'some_string'}]
        dg = [{'metadata': [{'a': 'string'}]}, {'data': [['some_string']]}]
        test_params.append(['simple_string', copy.deepcopy(fj), copy.deepcopy(dg)])

        # Null for string
        fj = [{'a': 'some_string', 'b': None}, {'a': 'one_more', 'b': 'string!'}]
        dg = [{'metadata': [{'a': 'string'}, {'b': 'string'}]}, {'data': [['some_string', None], ['one_more', 'string!']]}]
        test_params.append(['string_null', copy.deepcopy(fj), copy.deepcopy(dg)])

        return test_params

    def setup_method(self):
        pass


    @parameterized.expand(define_test_data())
    def test_bidir_json2dg(self, name, fj, dg):
        # Output of fromFlatJSON and toFlatJSON is string, but must be converted to json with no errors
        out_dg = sasdgfunc.fromFlatJSON(fj)
        assert out_dg == dg

    @parameterized.expand(define_test_data())
    def test_bidir_dg2json(self, name, fj, dg):
        # Output of fromFlatJSON and toFlatJSON is string, but must be converted to json with no errors
        out_fj = sasdgfunc.toFlatJSON(dg)
        assert out_fj == fj

    # Datagrid without data part
    def test_dg2json__nodata(self):
        dg = [{'metadata': []}]
        fj = []

        out_fj = sasdgfunc.toFlatJSON(dg)
        assert out_fj == fj

    def test_json2dg__bool(self):
        fj = [{'a': 'some_string', 'b': True}, {'a': 'one_more', 'b': False}]
        dg = [{'metadata': [{'a': 'string'}, {'b': 'decimal'}]}, {'data': [['some_string', 1], ['one_more', 0]]}]

        out_dg = sasdgfunc.fromFlatJSON(fj)
        assert out_dg == dg

    def test_json2dg__none(self):
        fj = [{'a': 'some_string', 'b': None}, {'a': 'one_more', 'b': None}]
        dg = [{'metadata': [{'a': 'string'}, {'b': 'string'}]}, {'data': [['some_string', None], ['one_more', None]]}]

        out_dg = sasdgfunc.fromFlatJSON(fj)
        assert out_dg == dg

    # Exceptions
    def test_json2dg__not_list(self):
        fj = {'a': 'one_more', 'b': 100}

        with pytest.raises(TypeError) as cm:
            out_dg = sasdgfunc.fromFlatJSON(fj)
        assert str(cm.value) == 'Expected: list, but received: <class \'dict\'>'

    def test_json2dg__not_dict_in_list(self):
        fj = ['not_dict', {'a': 'one_more', 'b': 100}]

        with pytest.raises(TypeError) as cm:
            out_dg = sasdgfunc.fromFlatJSON(fj)
        assert str(cm.value) == 'Each item must be of dict type'

    def test_json2dg__nonscalar_dict(self):
        fj = [{'a': 'some_string'}, {'a': 'one_more', 'b': {'c': 100, 'd': 200}}]

        with pytest.raises(TypeError) as cm:
            out_dg = sasdgfunc.fromFlatJSON(fj)
        assert str(cm.value) == 'Every dict must contain only int, float, str, bool items'

    def test_json2dg__nonscalar_list(self):
        fj = [{'a': 'some_string'}, {'a': 'one_more', 'b': [100, 200, 300]}]

        with pytest.raises(TypeError) as cm:
            out_dg = sasdgfunc.fromFlatJSON(fj)
        assert str(cm.value) == 'Every dict must contain only int, float, str, bool items'

    def test_json2dg__type_mismatch(self):
        fj = [{'a': 'some_string', 'b': 7}, {'a': 'one_more', 'b': 'string!'}]

        with pytest.raises(TypeError) as cm:
            out_dg = sasdgfunc.fromFlatJSON(fj)
        assert str(cm.value) == 'Type mismatch for key b. Found string! but expected <class \'float\'>'
