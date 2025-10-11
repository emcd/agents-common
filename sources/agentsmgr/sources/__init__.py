# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Source handlers for data location resolution.

    This package provides pluggable source handlers for resolving various
    types of data sources including local paths, Git repositories, and
    remote URLs to local filesystem paths.
'''


from .base import AbstractSourceHandler
from .base import resolve_source_location
from .base import register_source_handler
from .base import source_handler
from .local import LocalSourceHandler
from .git import GitSourceHandler


# Source handlers register themselves when their modules are imported