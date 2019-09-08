# coding: utf-8


class Dict(dict):

    def get_in(self, key=None, default=None):
        """Return value from a nested-map through key."""
        if key is None:
            raise KeyError("'Dict' attribute key can't be empty")
        key_list = key.strip().split('.')
        data = self
        size = len(key_list)
        for index, k in enumerate(key_list):
            data = data.get(k)
            if index < size-1 and not isinstance(data, dict):
                return default
        return data


def zipmap(keys, values):
    """Returns a map with the keys mapped to the corresponding values."""
    z = zip(keys, values)
    data = {k: v for k, v in z}
    return data






