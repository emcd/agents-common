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


''' Result objects for CLI command outputs with Markdown rendering. '''


from . import __


class ResultBase( __.immut.DataclassObject ):
    ''' Base protocol for command result objects with rendering capability. '''

    @__.abc.abstractmethod
    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders result as Markdown lines for display. '''
        raise NotImplementedError


class ConfigurationDetectionResult( ResultBase ):
    ''' Agent configuration detection result with formatted output. '''

    target: __.Path
    coders: tuple[ str, ... ]
    languages: tuple[ str, ... ]
    project_name: __.typx.Optional[ str ] = None

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders configuration detection as Markdown lines. '''
        lines = [ '🔍 Agent Configuration Detected:' ]
        lines.append( f"   Coders: {', '.join( self.coders )}" )
        lines.append( f"   Languages: {', '.join( self.languages )}" )
        if self.project_name:
            lines.append( f"   Project: {self.project_name}" )
        lines.append( f"   Target Directory: {self.target.resolve( )}" )
        return tuple( lines )


class ContentGenerationResult( ResultBase ):
    ''' Agent content generation result with formatted summary. '''

    source_location: __.Path
    target_location: __.Path
    coders: tuple[ str, ... ]
    simulated: bool
    items_generated: int = 0

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders content generation results as Markdown lines. '''
        lines = [ f"🚀 Populating agent content (simulate={self.simulated}):" ]
        lines.append( f"   Source: {self.source_location}" )
        lines.append( f"   Target: {self.target_location.resolve( )}" )
        lines.append( f"   Coders: {', '.join( self.coders )}" )
        lines.append( '' )
        lines.append( f"   Generated {self.items_generated} items" )
        lines.append( '' )
        if self.simulated:
            lines.append(
                "✅ Simulation complete. Use --no-simulate to write." )
        else:
            lines.append( "✅ Content generation complete." )
        return tuple( lines )


class ValidationResult( ResultBase ):
    ''' Template validation result with formatted summary. '''

    variant: str
    temporary_directory: __.Path
    items_attempted: int
    items_generated: int
    preserved: bool

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders validation results as Markdown lines. '''
        lines = [ f"✅ Validation complete for '{self.variant}' variant:" ]
        lines.append( f"   Temporary Directory: {self.temporary_directory}" )
        lines.append(
            f"   Items: {self.items_generated}/{self.items_attempted} "
            "generated" )
        if self.preserved:
            lines.append(
                f"   📁 Files preserved for inspection at: "
                f"{self.temporary_directory}" )
        else:
            lines.append( "   🗑️  Temporary files cleaned up" )
        return tuple( lines )