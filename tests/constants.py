test_string = "abcdefg"
test_int = 1234
test_float = 12.34
test_list_ints = [1, 2, 3, 4]
test_list_strs = ["a", "b", "c", "d"]
test_dictionary = {"a": 1, "b": 2, "c": 3, "d": 4}

test_numbers = {test_int, test_float}

test_tuple = (*test_numbers, test_string)

test_lists = [test_list_ints, test_list_strs]
test_sequences = [*test_lists, test_tuple]
