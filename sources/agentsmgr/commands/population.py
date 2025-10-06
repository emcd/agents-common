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


''' Command for populating agent content from data sources. '''


from . import __
from . import base as _base
from . import generator as _generator
from . import globalization as _globalization
from . import operations as _operations


_scribe = __.provide_scribe( __name__ )


class PopulateCommand( __.appcore_cli.Command ):
    ''' Generates dynamic agent content from data sources. '''

    source: __.typx.Annotated[
        str,
        __.tyro.conf.arg( help = "Data source (local path or git URL)" ),
    ] = '.'
    target: __.typx.Annotated[
        __.Path,
        __.tyro.conf.arg( help = "Target directory for content generation" ),
    ] = __.dcls.field( default_factory = __.Path.cwd )
    simulate: __.typx.Annotated[
        bool,
        __.tyro.conf.arg( help = "Dry run mode - show generated content" ),
    ] = True
    mode: __.typx.Annotated[
        __.TargetingMode,
        __.tyro.conf.arg( help = "Targeting mode: per-user or per-project" ),
    ] = 'per-project'
    update_globals: __.typx.Annotated[
        bool,
        __.tyro.conf.arg(
            help = "Update per-user global files (orthogonal to mode)" ),
    ] = False

    @_base.intercept_errors( )
    async def execute( self, auxdata: __.appcore.state.Globals ) -> None:  # pyright: ignore[reportIncompatibleMethodOverride]
        ''' Generates content from data sources and displays result. '''
        if not isinstance( auxdata, __.Globals ):  # pragma: no cover
            raise __.ContextInvalidity
        _scribe.info(
            f"Populating agent content from {self.source} to {self.target}" )
        configuration = await _base.retrieve_configuration( self.target )
        coder_count = len( configuration[ 'coders' ] )
        _scribe.debug( f"Detected configuration with {coder_count} coders" )
        _scribe.debug( f"Using {self.mode} targeting mode" )
        location = _base.retrieve_data_location( self.source )
        generator = _generator.ContentGenerator(
            location = location,
            configuration = configuration,
            application_configuration = auxdata.configuration,
            mode = self.mode,
        )
        items_attempted, items_generated = _operations.populate_directory(
            generator, self.target, self.simulate )
        _scribe.info( f"Generated {items_generated}/{items_attempted} items" )
        if self.update_globals:
            globals_attempted, globals_updated = (
                _globalization.populate_globals(
                    location,
                    configuration[ 'coders' ],
                    auxdata.configuration,
                    self.simulate,
                ) )
            _scribe.info(
                f"Updated {globals_updated}/{globals_attempted} "
                "global files" )
        result = __.ContentGenerationResult(
            source_location = location,
            target_location = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            simulated = self.simulate,
            items_generated = items_generated,
        )
        await __.render_and_print_result(
            result, auxdata.display, auxdata.exits )
