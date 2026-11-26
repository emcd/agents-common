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


''' Command for populating agent content from data sources.

    Also provides the generate command for maintainer-facing generation
    from components/ to distribution/.
'''


from .commands import GenerateCommand
from .commands import PopulateCommand
from .commands import PopulateProjectCommand
from .commands import PopulateUserCommand
from .commands import _manage_project_auxiliaries
from .commands import _populate_per_user_content
from .configurations import SourceArgument
from .configurations import TargetArgument
from .configurations import _coders_include
from .configurations import _filter_coders_by_mode
from .configurations import _format_exclude_path
from .configurations import _produce_default_configuration
from .configurations import _within_project_root
from .copying import SUPPORT_SCRIPTS
from .copying import _copy_distribution_items
from .copying import _copy_instructions_from_distribution
from .copying import _copy_skills
from .copying import _copy_support_scripts_from_distribution
from .copying import _copy_tree
from .copying import _support_script_excludes
from .linking import _canonical_skills_directory
from .linking import _create_all_symlinks
from .linking import _create_coder_directory_symlinks
from .linking import _ensure_directory_symlink
from .linking import _link_skills_discovery
