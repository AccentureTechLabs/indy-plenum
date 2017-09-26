from plenum.common.messages.fields import FieldBase, Base58Field


class PublicAddressField(FieldBase):
    _base_types = (str, )
    _public_address = Base58Field(byte_lengths=(32,))

    def _specific_validation(self, val):
        return self._public_address.validate(val)


class PublicAmountField(FieldBase):

    _base_types = (int, float)

    def _specific_validation(self, val):
        if val <= 0:
            return 'negative or zero value'


class PublicOutputField(FieldBase):
    _base_types = (list, tuple)
    _length = 2
    public_address_field = PublicAddressField()
    public_amount_field = PublicAmountField()

    def _specific_validation(self, val):
        if len(val) != self._length:
            return "should have length {}".format(self._length)
        addr_error = self.public_address_field.validate(val[0])
        if addr_error:
            return addr_error
        amt_error = self.public_amount_field.validate(val[1])
        if amt_error:
            return amt_error
