import torch
from collections import OrderedDict


class Parameter(torch.Tensor):
    r"""A kind of Tensor that is to be considered a module parameter.

    Parameters are :class:`~torch.Tensor` subclasses, that have a
    very special property when used with :class:`Module` s - when they're
    assigned as Module attributes they are automatically added to the list of
    its parameters, and will appear e.g. in :meth:`~Module.parameters` iterator.
    Assigning a Tensor doesn't have such effect. This is because one might
    want to cache some temporary state, like last hidden state of the RNN, in
    the model. If there was no such class as :class:`Parameter`, these
    temporaries would get registered too.

    Arguments:
        data (Tensor): parameter tensor.
        requires_grad (bool, optional): if the parameter requires gradient. See
            :ref:`excluding-subgraphs` for more details. Default: `True`
        tags (dict, optional): special information about this parameter (e.g.
            which optimizer to use). Note that `tags` are not included in
            the parameter's containing module's `.state_dict()`. Default: `None`
    """

    def __new__(cls, data=None, requires_grad=True, tags=None):
        if data is None:
            data = torch.Tensor()
        instance = torch.Tensor._make_subclass(cls, data, requires_grad)
        instance.tags = {} if tags is None else tags
        return instance

    def __deepcopy__(self, memo):
        if id(self) in memo:
            return memo[id(self)]
        else:
            result = type(self)(self.data.clone(memory_format=torch.preserve_format), self.requires_grad, self.tags)
            memo[id(self)] = result
            return result

    def __repr__(self):
        return 'Parameter containing:\n' + super(Parameter, self).__repr__()

    def __reduce_ex__(self, proto):
        # See Note [Don't serialize hooks]
        if self.tags:
            return (
                torch._utils._rebuild_parameter,
                (self.data, self.requires_grad, OrderedDict(), self.tags)
            )
        else:
            # This ensures that parameter without tags can be deserialized
            # by older version of PyTorch (i.e. forward compatibility)
            return (
                torch._utils._rebuild_parameter,
                (self.data, self.requires_grad, OrderedDict())
            )
