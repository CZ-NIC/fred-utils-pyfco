import warnings

from .name_service import CorbaNameServiceClient, init_omniorb_exception_handles

__all__ = ['CorbaNameServiceClient', 'init_omniorb_exception_handles']

warnings.warn("Model 'pyfco.corba' moved to 'pyfco.name_service'.", DeprecationWarning)
