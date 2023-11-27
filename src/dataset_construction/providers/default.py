from typing import List, Tuple, Union, Dict

class Query:
    """
    This is a base class for all queries. It provides a common structure for queries as well as a method for executing the query.
    
    Required methods:
        - execute: execute the query

    Optional methods:
        - __str__: string representation of the query (defaults to __dict__.__str__)
        - __repr__: representation of the query (defaults to __str__)
    
    Required attributes:
        - parameters: list of query parameters for the query
    """
    def __init__(self, query_parameters):
        self.parameters : Dict = query_parameters

    def __str__(self):
        return self.__dict__.__str__()
    
    def __repr__(self):
        return self.__str__()

class BaseEndpoint:
    """
    This is a base class for all endpoints. It provides a common interface for constructing and executing queries.

    Required methods:
        - _construct_query: construct a query for the endpoint
        - _execute_query: execute a query on the endpoint
        - query: construct and execute a query on the endpoint

    Optional methods:
        - authenticate: authenticate the endpoint (defaults to no authentication)

    Required attributes:
        - name: name of the endpoint
        - description: description of the endpoint
        - sub_url: sub_url for the endpoint
        - query_parameters: list of query parameters (QueryParameter) for the endpoint

    Optional attributes:
        - citation: citation for the endpoint (defaults to provider citation)
        - license: license for the endpoint (defaults to provider license)
        - delimiter: delimiter for the endpoint (defaults to "&")
    """
    def __init__(self, provider, name, description, sub_url, query_parameters, citation=None, license=None, delimiter="&"):
        self.provider = provider
        self.name = name
        self.description = description
        self.sub_url = sub_url
        self.query_parameters = query_parameters
        self.delimiter = delimiter
        self.citation = citation if citation else provider.citation
        self.license = license if license else provider.license
        self._do_authentication = False

    def _construct_query(self, **kwargs) -> Query:
        raise NotImplementedError
    
    def _execute(self, query: Query):
        raise NotImplementedError

    def _execute_query(self, query: Query, authenticate : bool = False):
        # If authentication is required, authenticate
        if authenticate:
            auth_result = self.authenticate()
            # Log authentication result
            self.provider.log(auth_result[1])
            # If authentication failed, raise exception
            if not auth_result[0]:
                raise Exception(auth_result[1])
        # Log query
        self.provider.log(query)
        result = self._execute(query)
        # Log result
        self.provider.log(result)
        return result

    def authenticate(self) -> Tuple[bool, str]:
        raise NotImplementedError("Authentication is not implemented for this endpoint, and should not be called.")

    def query(self, **kwargs):
        """
        This is as simple wrapper for _construct_query and _execute_query. It constructs a query using _construct_query and executes it using _execute_query.

        Args:
            **kwargs: keyword arguments for _construct_query (most likely query parameters, see _construct_query for more information)
        """
        return self._execute_query(self._construct_query(**kwargs), authenticate=self._do_authentication)
        

class BaseProviderClass:
    """
    This is a base class for all data providers. It provides a common interface for querying data.
    
    Required methods:
        - search: search the data provider for metadata that matches the query
        - fetch: fetch data from the provider that matches the query
        - log: log queries and results to a log-file
    
    Required attributes:
        - name: name of the provider
        - description: description of the provider
        - citation: citation for the provider
        - license: license for the provider
        - url: url for the provider
        - endpoints: list of endpoints (Endpoint) for the provider
    """
    def __init__(self, name, description, citation, license, url, endpoints):
        self.name = name
        self.description = description
        self.citation = citation
        self.license = license
        self.url = url
        self.endpoints : List[BaseEndpoint] = endpoints
        self._logger = lambda x: None
    
    def search(self, query : Query):
        raise NotImplementedError
    
    def fetch(self, query : Query):
        raise NotImplementedError
    
    def log(self, what):
        """
        This function logs the given string to the log file.

        Args:
            what: An object that can be converted to a string.
        
        Returns:
            The string that was logged.
        """
        if not callable(getattr(what, "__str__", None)):
            raise TypeError("Cannot log object of type {} as it does not have a __str__ method.".format(type(what)))
        log_str = what.__str__()
        self._logger(log_str)
        return log_str
