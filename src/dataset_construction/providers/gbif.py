import os
import json
from typing import Any, Tuple
import requests
from requests.auth import HTTPBasicAuth

from default import BaseProviderClass, BaseEndpoint, Query
from typing import List, Tuple, Union, Dict, Any

class GBIF_API_V1_Endpoint(BaseEndpoint):
    """
    This is a base class for all GBIF API v1 endpoints. It provides a common interface for constructing and executing queries.

    Required properties:
        - description: description of the endpoint
    """
    def __init__(self, provider : "GBIF_API_V1", name : str, sub_url : str):
        super().__init__(
            provider=provider,
            name=name,
            sub_url=sub_url
        )
        self._do_authentication = True
        self.endpoint_delimiter = "/"
        self.arguments_delimiter = "&"
        self.endpoint_arguments_delimiter = "?"
    
    def authenticate(self) -> Tuple[bool, HTTPBasicAuth]:
        return self.provider.authenticate()
    
    def _construct_query(self, subendpoints : List, parameters : dict) -> Query:
        return Query(subendpoints=subendpoints, parameters=parameters)
    
    def _execute(self, query: Query, authentication : HTTPBasicAuth = None, timeout : Union[int, None] = None) -> Tuple[bool, Any]:
        if not isinstance(query, Query):
            raise TypeError(f"Expected query of type Query, got {type(query)}")
        if not isinstance(authentication, HTTPBasicAuth):
            raise TypeError(f"Expected authentication of type HTTPBasicAuth, got {type(authentication)}")
        base_url = [self.provider.url, self.sub_url] + query.subendpoints
        base_url = self.endpoint_delimiter.join(base_url)
        arguments = self.arguments_delimiter.join([f"{key}={value}" for key, value in query.parameters.items()])
        url = base_url + self.endpoint_arguments_delimiter + arguments
        self.provider._logger(f"Querying {url}")
        response = requests.get(url, auth=authentication, timeout=timeout)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.text
        
    def query(self, subendpoints : List[str], parameters : Dict, timeout : Union[int, None] = None) -> Tuple[bool, Any]:
        """
        Query the GBIF v1 API at the selected endpoint.

        See endpoint.description for more information on the endpoint, subendpoints, and parameters.

        Arguments:
            - subendpoints: list of subendpoints to query
            - parameters: dictionary of parameters and values to query.
            - timeout: timeout for the query (seconds). Default: No timeout.
        """
        return super().query(execute_args={"timeout": timeout}, subendpoints=subendpoints, parameters=parameters)

class GBIF_API_V1_Registry(GBIF_API_V1_Endpoint):
    def __init__(self, provider):
        super().__init__(
            provider=provider,
            name="GBIF Registry",
            sub_url="registry"
        )

    @property
    def description(self) -> str:
        """
        This API works against the GBIF Registry, which makes all registered Datasets, Installations, Organizations, Nodes, and Networks discoverable.

        Internally we use a Java web service client for the consumption of these HTTP-based, RESTful web services. It may be of interest to those coding against the API, and can be found in the registry-ws-client project.

        Please note the old Registry API is still supported, but is now deprecated. Anyone starting new work is strongly encouraged to use the new API.
        
        See https://www.gbif.org/developer/registry for more information on the GBIF Registry, subendpoints, and query parameters.
        """
        return GBIF_API_V1_Registry.description.__doc__
    
class GBIF_API_V1_Species(GBIF_API_V1_Endpoint):
    def __init__(self, provider):
        super().__init__(
            provider=provider,
            name="GBIF Species",
            sub_url="species"
        )

    @property
    def description(self) -> str:
        """
        This API works against data kept in the GBIF Checklist Bank which taxonomically indexes all registered checklist datasets in the GBIF network.

        For statistics on checklist datasets, you can refer to the dataset metrics section of the Registry API.

        Internally we use a Java web service client for the consumption of these HTTP-based, RESTful JSON web services.

        See https://www.gbif.org/developer/species for more information on the GBIF Species, subendpoints, and query parameters.
        """
        return GBIF_API_V1_Species.description.__doc__
    
class GBIF_API_V1_Occurrence(GBIF_API_V1_Endpoint):
    def __init__(self, provider):
        super().__init__(
            provider=provider,
            name="GBIF Occurrence",
            sub_url="occurrence"
        )
    
    @property
    def description(self) -> str:
        """
        This API works against the GBIF Occurrence Store, which handles occurrence records and makes them available through the web service and download files. In addition we also provide a Map API that offers spatial services.

        Internally we use a Java web service client for the consumption of these HTTP-based, RESTful web services.

        See https://www.gbif.org/developer/occurrence for more information on the GBIF Occurrence, subendpoints, and query parameters.
        """
        return GBIF_API_V1_Occurrence.description.__doc__
    
class GBIF_API_V1_Maps(GBIF_API_V1_Endpoint):
    def __init__(self, provider):
        super().__init__(
            provider=provider,
            name="GBIF Maps",
            sub_url="maps"
        )

    @property
    def description(self):
        """
        # NOT IMPLEMENTED YET

        ### Feature overview

        The following features are supported:

            * Map layers are available for a country, dataset, taxon (including species, subspecies or higher taxon), publisher, publishing country or network. These layers can be filtered by year range, basis of record and country.
            * Data is returned as points, or "binned" into hexagons or squares.
            * Four map projections are supported.
            * Tiles are available in vector format for client styling, or raster format with predefined styles.
            * Arbitrary search terms are also supported, limited to a single projection and forced binning.
        
        This service is intended for use with commonly used clients such as the OpenLayers or Leaflet Javascript libraries, Google Maps, or some GIS software. 
        These libraries allow the GBIF layers to be visualized with other content, such as those coming from web map service (WMS) providers. 
        It should be noted that the mapping API is not a WMS service, nor does it support WFS capabilities.

        See https://www.gbif.org/developer/maps for more information on the GBIF Maps, subendpoints, and query parameters.
        """    
    
    def _execute(self):
        raise NotImplementedError("Maps is not implemented yet.")

class GBIF_API_V1(BaseProviderClass):
    """
    A class for the GBIF API v1.

    Attributes:
        - user, password: credentials for the GBIF API v1. Preferably set as environment variables GBIF_USER and GBIF_PASSWORD.
        - url: https://api.gbif.org/v1
        - name: GBIF API v1
        - citation: Too long to fit here, see citation property.
        - description: Too long to fit here, see description property.
        - license: Too long to fit here, see license property.
        - endpoints: dict of endpoints (Endpoint) for the provider

    Methods:
        - authenticate: authenticate with the GBIF API v1 using Basic HTTP Authentication (is called internally when )

    ----------------------------------------------------

    ### Description
    The GBIF API is a RESTful JSON based API. The base URL for v1 you should use is: https://api.gbif.org/v1/
    
    The API is split into logical sections (endpoints) to ease understanding:

        - Registry: Provides means to create, edit, update and search for information about the datasets, organizations (e.g. data publishers), networks and the means to access them (technical endpoints). 
          The registered content controls what is crawled and indexed in the GBIF data portal, but as a shared API may also be used for other initiatives
        - Species: Provides services to discover and access information about species and higher taxa, and utility services for interpreting names and looking up the identifiers and complete scientific names used for species in the GBIF portal.
        - Occurrence: Provides access to occurrence information crawled and indexed by GBIF and search services to do real time paged search and asynchronous download services to do large batch downloads.
        - Maps: Provides simple services to show the maps of GBIF mobilized content on other sites.

    ### Credit
    Description modified from https://www.gbif.org/developer/summary, updated information and full documentation can be found there.
    """
    def __init__(self, user : Union[str, None] = None, password : Union[str, None] = None):
        super().__init__()
        if not user is None or not password is not None:
            print("Warning: User or password provided, consider using environment variables GBIF_USER and GBIF_PASSWORD instead.")
            assert isinstance(user, str) or user is None, "User must be a string or None."
            assert isinstance(password, str) or password is None, "Password must be a string or None."
        self.user = os.getenv("GBIF_USER") if user is None else user
        self.password = os.getenv("GBIF_PASSWORD") if password is None else password
        self._endpoints : Dict[str, GBIF_API_V1_Endpoint] = {
            "registry": GBIF_API_V1_Registry(self),
            "species": GBIF_API_V1_Species(self),
            "occurrence": GBIF_API_V1_Occurrence(self),
            "maps": GBIF_API_V1_Maps(self)
        }
        # print("Proper logger not implemented yet, using print instead.")
        # self._logger = print

    def authenticate(self) -> Tuple[bool, HTTPBasicAuth]:
        return True, HTTPBasicAuth(self.user, self.password)
    
    @property
    def url(self):
        """https://api.gbif.org/v1"""
        return GBIF_API_V1.url.__doc__

    @property
    def name(self):
        """GBIF API v1"""
        return GBIF_API_V1.name.__doc__
    
    @property
    def citation(self):
        """
        GBIF: The Global Biodiversity Information Facility (year) What is GBIF?. Available from https://www.gbif.org/what-is-gbif [13 January 2020]
        """
        return GBIF_API_V1.citation.__doc__
    
    @property
    def description(self):
        '''
        The GBIF API is a RESTful JSON based API. The base URL for v1 you should use is: https://api.gbif.org/v1/

        The API is split into logical sections (endpoints) to ease understanding:

            - Registry: Provides means to create, edit, update and search for information about the datasets, organizations (e.g. data publishers), networks and the means to access them (technical endpoints). The registered content controls what is crawled and indexed in the GBIF data portal, but as a shared API may also be used for other initiatives
            - Species: Provides services to discover and access information about species and higher taxa, and utility services for interpreting names and looking up the identifiers and complete scientific names used for species in the GBIF portal.
            - Occurrence: Provides access to occurrence information crawled and indexed by GBIF and search services to do real time paged search and asynchronous download services to do large batch downloads.
            - Maps: Provides simple services to show the maps of GBIF mobilized content on other sites.

        ### Credit
        Description modified from https://www.gbif.org/developer/summary, updated information and full documentation can be found there.\
        '''
        return GBIF_API_V1.description.__doc__
    
    @property 
    def license(self):
        '''
        Apache License
                                Version 2.0, January 2004
                                http://www.apache.org/licenses/

        TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

        1. Definitions.

            "License" shall mean the terms and conditions for use, reproduction,
            and distribution as defined by Sections 1 through 9 of this document.

            "Licensor" shall mean the copyright owner or entity authorized by
            the copyright owner that is granting the License.

            "Legal Entity" shall mean the union of the acting entity and all
            other entities that control, are controlled by, or are under common
            control with that entity. For the purposes of this definition,
            "control" means (i) the power, direct or indirect, to cause the
            direction or management of such entity, whether by contract or
            otherwise, or (ii) ownership of fifty percent (50%) or more of the
            outstanding shares, or (iii) beneficial ownership of such entity.

            "You" (or "Your") shall mean an individual or Legal Entity
            exercising permissions granted by this License.

            "Source" form shall mean the preferred form for making modifications,
            including but not limited to software source code, documentation
            source, and configuration files.

            "Object" form shall mean any form resulting from mechanical
            transformation or translation of a Source form, including but
            not limited to compiled object code, generated documentation,
            and conversions to other media types.

            "Work" shall mean the work of authorship, whether in Source or
            Object form, made available under the License, as indicated by a
            copyright notice that is included in or attached to the work
            (an example is provided in the Appendix below).

            "Derivative Works" shall mean any work, whether in Source or Object
            form, that is based on (or derived from) the Work and for which the
            editorial revisions, annotations, elaborations, or other modifications
            represent, as a whole, an original work of authorship. For the purposes
            of this License, Derivative Works shall not include works that remain
            separable from, or merely link (or bind by name) to the interfaces of,
            the Work and Derivative Works thereof.

            "Contribution" shall mean any work of authorship, including
            the original version of the Work and any modifications or additions
            to that Work or Derivative Works thereof, that is intentionally
            submitted to Licensor for inclusion in the Work by the copyright owner
            or by an individual or Legal Entity authorized to submit on behalf of
            the copyright owner. For the purposes of this definition, "submitted"
            means any form of electronic, verbal, or written communication sent
            to the Licensor or its representatives, including but not limited to
            communication on electronic mailing lists, source code control systems,
            and issue tracking systems that are managed by, or on behalf of, the
            Licensor for the purpose of discussing and improving the Work, but
            excluding communication that is conspicuously marked or otherwise
            designated in writing by the copyright owner as "Not a Contribution."

            "Contributor" shall mean Licensor and any individual or Legal Entity
            on behalf of whom a Contribution has been received by Licensor and
            subsequently incorporated within the Work.

        2. Grant of Copyright License. Subject to the terms and conditions of
            this License, each Contributor hereby grants to You a perpetual,
            worldwide, non-exclusive, no-charge, royalty-free, irrevocable
            copyright license to reproduce, prepare Derivative Works of,
            publicly display, publicly perform, sublicense, and distribute the
            Work and such Derivative Works in Source or Object form.

        3. Grant of Patent License. Subject to the terms and conditions of
            this License, each Contributor hereby grants to You a perpetual,
            worldwide, non-exclusive, no-charge, royalty-free, irrevocable
            (except as stated in this section) patent license to make, have made,
            use, offer to sell, sell, import, and otherwise transfer the Work,
            where such license applies only to those patent claims licensable
            by such Contributor that are necessarily infringed by their
            Contribution(s) alone or by combination of their Contribution(s)
            with the Work to which such Contribution(s) was submitted. If You
            institute patent litigation against any entity (including a
            cross-claim or counterclaim in a lawsuit) alleging that the Work
            or a Contribution incorporated within the Work constitutes direct
            or contributory patent infringement, then any patent licenses
            granted to You under this License for that Work shall terminate
            as of the date such litigation is filed.

        4. Redistribution. You may reproduce and distribute copies of the
            Work or Derivative Works thereof in any medium, with or without
            modifications, and in Source or Object form, provided that You
            meet the following conditions:

            (a) You must give any other recipients of the Work or
                Derivative Works a copy of this License; and

            (b) You must cause any modified files to carry prominent notices
                stating that You changed the files; and

            (c) You must retain, in the Source form of any Derivative Works
                that You distribute, all copyright, patent, trademark, and
                attribution notices from the Source form of the Work,
                excluding those notices that do not pertain to any part of
                the Derivative Works; and

            (d) If the Work includes a "NOTICE" text file as part of its
                distribution, then any Derivative Works that You distribute must
                include a readable copy of the attribution notices contained
                within such NOTICE file, excluding those notices that do not
                pertain to any part of the Derivative Works, in at least one
                of the following places: within a NOTICE text file distributed
                as part of the Derivative Works; within the Source form or
                documentation, if provided along with the Derivative Works; or,
                within a display generated by the Derivative Works, if and
                wherever such third-party notices normally appear. The contents
                of the NOTICE file are for informational purposes only and
                do not modify the License. You may add Your own attribution
                notices within Derivative Works that You distribute, alongside
                or as an addendum to the NOTICE text from the Work, provided
                that such additional attribution notices cannot be construed
                as modifying the License.

            You may add Your own copyright statement to Your modifications and
            may provide additional or different license terms and conditions
            for use, reproduction, or distribution of Your modifications, or
            for any such Derivative Works as a whole, provided Your use,
            reproduction, and distribution of the Work otherwise complies with
            the conditions stated in this License.

        5. Submission of Contributions. Unless You explicitly state otherwise,
            any Contribution intentionally submitted for inclusion in the Work
            by You to the Licensor shall be under the terms and conditions of
            this License, without any additional terms or conditions.
            Notwithstanding the above, nothing herein shall supersede or modify
            the terms of any separate license agreement you may have executed
            with Licensor regarding such Contributions.

        6. Trademarks. This License does not grant permission to use the trade
            names, trademarks, service marks, or product names of the Licensor,
            except as required for reasonable and customary use in describing the
            origin of the Work and reproducing the content of the NOTICE file.

        7. Disclaimer of Warranty. Unless required by applicable law or
            agreed to in writing, Licensor provides the Work (and each
            Contributor provides its Contributions) on an "AS IS" BASIS,
            WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
            implied, including, without limitation, any warranties or conditions
            of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
            PARTICULAR PURPOSE. You are solely responsible for determining the
            appropriateness of using or redistributing the Work and assume any
            risks associated with Your exercise of permissions under this License.

        8. Limitation of Liability. In no event and under no legal theory,
            whether in tort (including negligence), contract, or otherwise,
            unless required by applicable law (such as deliberate and grossly
            negligent acts) or agreed to in writing, shall any Contributor be
            liable to You for damages, including any direct, indirect, special,
            incidental, or consequential damages of any character arising as a
            result of this License or out of the use or inability to use the
            Work (including but not limited to damages for loss of goodwill,
            work stoppage, computer failure or malfunction, or any and all
            other commercial damages or losses), even if such Contributor
            has been advised of the possibility of such damages.

        9. Accepting Warranty or Additional Liability. While redistributing
            the Work or Derivative Works thereof, You may choose to offer,
            and charge a fee for, acceptance of support, warranty, indemnity,
            or other liability obligations and/or rights consistent with this
            License. However, in accepting such obligations, You may act only
            on Your own behalf and on Your sole responsibility, not on behalf
            of any other Contributor, and only if You agree to indemnify,
            defend, and hold each Contributor harmless for any liability
            incurred by, or claims asserted against, such Contributor by reason
            of your accepting any such warranty or additional liability.

        END OF TERMS AND CONDITIONS




        Copyright 2014 Global Biodiversity Information Facility (GBIF)

        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.
        '''
        return GBIF_API_V1.license.__doc__
    
    @property
    def endpoints(self) -> Dict[str, GBIF_API_V1_Endpoint]:
        """
        * #### Registry:
          Provides means to create, edit, update and search for information about the datasets, organizations (e.g. data publishers), networks and the means to access them (technical endpoints). 
          The registered content controls what is crawled and indexed in the GBIF data portal, but as a shared API may also be used for other initiatives
        * #### Species:
          Provides services to discover and access information about species and higher taxa, and utility services for interpreting names and looking up the identifiers and complete scientific names used for species in the GBIF portal.
        * #### Occurrence:
          Provides access to occurrence information crawled and indexed by GBIF and search services to do real time paged search and asynchronous download services to do large batch downloads.
        * #### Maps:
          Provides simple services to show the maps of GBIF mobilized content on other sites.
        """
        return self._endpoints


test = GBIF_API_V1(
    user = "asvenning_au_workaccount",
    password="hp12rs123"
)

test_query = test.endpoints["species"].query(subendpoints=["suggest"], parameters={"q" : "Picea abies"})

print(test_query)