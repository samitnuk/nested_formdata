import unittest

from django.http import QueryDict

from drf_nested_formdata.utils import NestedFormDataSerializer



class NestedFormDataTestCase(unittest.TestCase):     

    def test_data_1(self):

        data_1 = {
            '[0][attribute]': 'size',
            '[0][verbose][0]': 'bazz',
            '[0][verbose][1]': 'foo',
            '[0][variant][vendor_metric]': '456',
            '[0][variant][metric_verbose_name]': 'Large',
            '[0][foo][baaz]': 'ggg',
            '[1][attribute]': 'size',
            '[1][verbose]': 'size',
            '[1][variant][vendor_metric]': 'L',
            '[1][variant][metric_verbose_name][foo][baaz][]': 'Large',
            '[1][foo][baaz]': 'true'
        }

        expected_output = [
            {
                'attribute': 'size', 
                'verbose': ['bazz', 'foo'], 
                'variant': {
                    'vendor_metric': 456, 
                    'metric_verbose_name': 'Large'
                }, 
                'foo': { 'baaz': 'ggg' }
            }, 
            {
                'attribute': 'size', 
                'verbose': 'size', 
                'variant': {
                    'vendor_metric': 'L', 
                    'metric_verbose_name': { 'foo': { 'baaz': ['Large'] } }
                }, 
                'foo': { 'baaz': True }
            }
        ]
    
        serializerObject = NestedFormDataSerializer(data_1)
        serializerObject.is_valid(raise_exception=True)
        self.assertEqual(len(serializerObject.data), 2)
        self.assertEqual(serializerObject.data, expected_output)

    
    def test_data_2(self):
        """
        a non nested data will not run
        """
        data_2 = {
            'vendor_metric': 'L',
            'attribute': 'size',
            'variant': 'color',
        }

        serializerObject = NestedFormDataSerializer(data_2)
        self.assertFalse(serializerObject.is_valid())

    def test_data_3(self):
        """
        if one or more data is nested in the form it will be valid
        """

        data_3 = {
            'vendor_metric': 'L',
            'attribute': 'size',
            '[variant][]': 'color',
        }

        expected_output = {
            'vendor_metric': 'L',
            'attribute': 'size',
            'variant': ['color']
        }
        serializerObject = NestedFormDataSerializer(data_3)
        self.assertTrue(serializerObject.is_valid())
        self.assertEqual(serializerObject.data, expected_output)


    def test_data_4(self):
        """
        test support for namespace if provided
        """

        data_4 = {
            'item[attribute][0][user_type]': 'size',
            'item[attribute][1][user_type]': '',
            'item[verbose][]': '',
            'item[variant][vendor_metric]': '[]',
            'item[variant][metric_verbose_name]': 'Large',
            'item[foo][baaz]': 'null',
        }

        expected_output = {
            'item': {
                'attribute': [
                    {'user_type': 'size'}, 
                    {'user_type': ''}
                ], 
                'verbose': [''], 
                'variant': {
                    'vendor_metric': None, 
                    'metric_verbose_name': 'Large'
                }, 
                'foo': { 'baaz': None }
                }
            }

        kwargs = {
            'allow_blank': True,
            'allow_empty': False
        }
        
        serializerObject = NestedFormDataSerializer(data_4, **kwargs)
        serializerObject.is_valid(raise_exception=True)
        self.assertTrue(isinstance(serializerObject.data['item'], dict))
        self.assertEqual(serializerObject.data, expected_output)

    def test_data_5(self):
        """
        test sparse array 
        """
        data_5 = {
            'item[attribute][0][user_type]': 'size',
            'item[attribute][3][user_type]': 'color',
            'item[attribute][6][user_type]': 'length',
        }

        expected_output = {
            'item': {
                'attribute': [
                    {'user_type': 'size'},
                    None,
                    None, 
                    {'user_type': 'color'},
                    None,
                    None,
                    {'user_type': 'length'}
                    ]
                }
            }
        serializerObject = NestedFormDataSerializer(data_5)
        serializerObject.is_valid(raise_exception=True)
        self.assertEqual(serializerObject.data, expected_output)

    def test_data_6(self):
        """
        test single object keys
        """
        data_6 = {
            'item[verbose][0][user_type_1]': 'seller',
            'item[verbose][0][user_type_2]': 'buyer',
        }

        expected_output = {
            'item': {
                'verbose':[{
                        'user_type_1': 'seller', 
                        'user_type_2': 'buyer'
                    }]
            }
        }
        serializerObject = NestedFormDataSerializer(data_6)
        serializerObject.is_valid(raise_exception=True)
        self.assertEqual(serializerObject.data, expected_output)

    def test_data_7(self):
        """
        Test even more complex and wicked data structure 
        i would prefer to avoid data structures like this` 
        """
        data_7 = {
            'item[attribute][0][user_type]': 'size',
            'item[attribute][1][user_type]': 'color',
            'item[verbose][]': '[]',
            'item[variant][vendor_metric]': 'Lego',
            'item[variant][metric_verbose_name]': 'Large',
            'item[foo][baaz]': 'null',
            'next[attribute][0][user_type]': 'people',
            'next[attribute][1][user_type]': 'color',
            'next[verbose][]': '{}',
            'next[variant][vendor_metric]': 'Leggit',
            'next[variant][metric_verbose_name]': 'Large',
            'next[foo][baaz]': 'null',
            '[variant][]': 'color',
            '[0][attribute]': 'size',
            '[0][verbose][0]': 'bazz',
            '[0][verbose][1]': 'foo',
            '[0][variant][vendor_metric]': '456',
            '[0][variant][metric_verbose_name]': 'Large',
            '[0][foo][baaz]': 'ggg',
        }

        expected_output = {
            'item': {
                    'attribute': [
                        {'user_type': 'size'}, 
                        {'user_type': 'color'}
                    ], 
                    'verbose': [None], 
                    'variant': {
                        'vendor_metric': 'Lego', 
                        'metric_verbose_name': 'Large'
                    }, 
                    'foo': {'baaz': None}
                },
            'next': {
                    'attribute': [
                        {'user_type': 'people'}, 
                        {'user_type': 'color'}
                        ], 
                    'verbose': [None], 
                    'variant': {
                        'vendor_metric': 'Leggit', 
                        'metric_verbose_name': 'Large'
                    }, 
                    'foo': { 'baaz': None }
                },
            'variant': ['color'],
            '': [{
                    'attribute': 'size', 
                    'verbose': ['bazz', 'foo'], 
                    'variant': {
                        'vendor_metric': 456, 
                        'metric_verbose_name': 'Large'
                    }, 
                    'foo': {'baaz': 'ggg'}
                }]
            }
        serializerObject = NestedFormDataSerializer(data_7)
        serializerObject.is_valid(raise_exception=True)
        self.assertEqual(serializerObject.data, expected_output)

    def test_data_8(self):
        """
        test same nested key with multiple value
        """

        data_8 = QueryDict(mutable=True)
        data_8.setlist('[variant][]', ['color', 'size'])
        data_8.setdefault('[verbose][0]', 'bazz')
        data_8.setdefault('[verbose][1]',  'foo')

        expected_output = {
            'variant': ['color', 'size'],
            'verbose': ['bazz', 'foo'] 
        }

        serializerObject = NestedFormDataSerializer(data_8)
        serializerObject.is_valid(raise_exception=True)
        self.assertEqual(serializerObject.data, expected_output)
