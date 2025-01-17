import re

# Nested Form data deserializer utility class
# --------------------------------------------


class UtilityMixin(object):
    _nested_re = re.compile(r'((.+)\[(.*)\]+)|(\[(.*)\]{2,})')
    _namespace_re = re.compile(r'^([\w]+)(?=\[)')
    _list_re = re.compile(r'\[([0-9]+)\]')
    _number_re = re.compile(r'[0-9]+')
    _dict_re = re.compile(r'\[(([^A-Za-z]*)([^0-9]+)([0-9]*))+\]')

    @staticmethod
    def strip_bracket(string=''):
        return string.replace('[', '').replace(']', '')

    @staticmethod
    def split_nested_str(string=''):
        subkeys = [key + ']' for key in string.split(']') if key != '']

        assert len(subkeys) > 0, ('Cannot split this key `%s`' % (string))

        return subkeys

    @staticmethod
    def str_is_empty_list(string=''):
        return string == '[]'

    @staticmethod
    def str_is_empty_dict(string=''):
        return string == '{}'

    def str_is_dict(self, string=''):
        return bool(self._dict_re.fullmatch(string))

    def str_is_list(self, string=''):
        return bool(self._list_re.fullmatch(string))

    def str_is_number(self, string=''):
        return bool(self._number_re.fullmatch(string))

    def str_is_nested(self, string=''):
        return bool(self._nested_re.fullmatch(string))

    def str_is_namespaced(self, string=''):
        return bool(self._namespace_re.match(string))

    def get_namespace(self, string=''):
        namespace = self._namespace_re.match(string)

        if namespace:
            return namespace.group(0)

        return None

    def strip_namespace(self, string=''):
        """
        Strip namespace from key if any 
        """
        namespace = self._namespace_re.match(string)

        if namespace:
            splited_string = string.split(namespace.group(1))

            assert len(splited_string) > 0, (
                'Cannot strip namespace from' 'this key `%s`' % (string)
            )

            string = ''.join(splited_string)

            return string

        return string

    def extract_index(self, string=''):
        number = self._number_re.search(string)

        if number:
            return int(number.group(0))

        return None

    def replace_specials(self, string):
        """
        Checks for and replaces special characters like null, booleans
        also changes numbers from string to integer
        """
        # the incoming value may not be a string sometimes
        if not isinstance(string, str):
            return string

        if string == 'null':
            return None
        elif string == 'true':
            return True
        elif string == 'false':
            return False
        elif self.str_is_number(string):
            return int(string)
        elif self.str_is_empty_list(string):
            return []
        elif self.str_is_empty_dict(string):
            return {}
        else:
            return string

    def get_container(self, key, index=0):
        """
        It return the appropiate container `[]`|`{}`
        based on the key provided
        """
        if self.str_is_nested(key):
            key = self.strip_namespace(key)
            sub_keys = self.split_nested_str(key)

            if self.str_is_list(sub_keys[index]):
                return []
            elif self.str_is_dict(sub_keys[index]):
                return {}
            else:
                return None
        else:
            return {}

    def key_is_last(self, current_key, data, is_type_of='non_nested'):
        """
        Checks if current key is the last in the data
        """
        keys = list(data.keys())
        current_index = keys.index(current_key)
        next_index = current_index + 1

        def object_type(is_obj):
            try:
                next_key = self.split_nested_str(keys[next_index])[0]
                if is_obj(next_key):
                    is_last = False
                else:
                    is_last = True
            except IndexError:
                is_last = True

            return is_last

        def namespace():
            try:
                next_key = keys[next_index]
                if self.str_is_namespaced(next_key):
                    current_namespace = self.get_namespace(current_key)
                    next_namespace = self.get_namespace(next_key)

                    if current_namespace == next_namespace:
                        is_last = False
                    else:
                        is_last = True
                else:
                    is_last = True
            except IndexError:
                is_last = True

            return is_last

        def ordinary():
            try:
                if not self.str_is_namespaced(keys[next_index]):
                    next_k = self.split_nested_str(keys[next_index])[0]

                    if not self.str_is_list(next_k) and not self.str_is_dict(next_k):
                        is_last = False
                    else:
                        is_last = True
                else:
                    is_last = True
            except IndexError:
                is_last = True

            return is_last

        if is_type_of == 'list':
            return object_type(self.str_is_list)
        elif is_type_of == 'namespace':
            return namespace()
        elif is_type_of == 'dict':
            return object_type(self.str_is_dict)
        else:
            return ordinary()
