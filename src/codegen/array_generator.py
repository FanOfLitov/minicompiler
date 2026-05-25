"""
Sprint 7: array layout and address generation helpers.
Compatible with Python 3.8+.
"""
from dataclasses import dataclass
from typing import List, Sequence


class ArrayLayoutError(ValueError):
    pass


TYPE_SIZES = {
    "bool": 1,
    "int": 8,
    "float": 8,
    "string": 8,
}


@dataclass
class ArrayLayout:
    name: str
    element_type: str
    dimensions: List[int]

    def __post_init__(self):
        if self.element_type not in TYPE_SIZES:
            raise ArrayLayoutError("unknown array element type '{}'".format(self.element_type))

        if not self.dimensions:
            raise ArrayLayoutError("array '{}' must have at least one dimension".format(self.name))

        for dim in self.dimensions:
            if dim <= 0:
                raise ArrayLayoutError("array '{}' has invalid dimension {}".format(self.name, dim))

    @property
    def element_size(self):
        return TYPE_SIZES[self.element_type]

    @property
    def element_count(self):
        result = 1
        for dim in self.dimensions:
            result *= dim
        return result

    @property
    def total_size(self):
        return self.element_count * self.element_size

    def flatten_index(self, indexes: Sequence[int]):
        if len(indexes) != len(self.dimensions):
            raise ArrayLayoutError(
                "array '{}' expects {} indexes, got {}".format(
                    self.name, len(self.dimensions), len(indexes)
                )
            )

        offset = 0
        stride = 1

        for index, dimension in zip(reversed(indexes), reversed(self.dimensions)):
            if index < 0 or index >= dimension:
                raise ArrayLayoutError(
                    "array '{}' index {} out of bounds for dimension {}".format(
                        self.name, index, dimension
                    )
                )

            offset += index * stride
            stride *= dimension

        return offset

    def byte_offset(self, indexes: Sequence[int]):
        return self.flatten_index(indexes) * self.element_size

    def address_expression(self, base_register: str, indexes: Sequence[int]):
        offset = self.byte_offset(indexes)
        if offset == 0:
            return "[{}]".format(base_register)
        return "[{}+{}]".format(base_register, offset)


class ArrayGenerator:
    def declare_static_array(self, name, element_type, dimensions):
        return ArrayLayout(name=name, element_type=element_type, dimensions=list(dimensions))

    def emit_bounds_check_comment(self, layout, indexes):
        layout.flatten_index(indexes)
        return "; bounds check ok for {}{}".format(layout.name, list(indexes))

    def emit_load(self, layout, base_register, indexes, target_register):
        return "mov {}, qword {}".format(target_register, layout.address_expression(base_register, indexes))

    def emit_store(self, layout, base_register, indexes, source_register):
        return "mov qword {}, {}".format(layout.address_expression(base_register, indexes), source_register)
