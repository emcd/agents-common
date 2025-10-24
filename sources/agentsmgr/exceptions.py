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


''' Family of exceptions for package API. '''


from . import __


class Omniexception( __.immut.exceptions.Omniexception ):
    ''' Base for all exceptions raised by package API. '''


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders exception as Markdown lines for display. '''
        return ( f"❌ {self}", )


class CoderAbsence( Omnierror, ValueError ):
    ''' Coder absence in registry. '''

    def __init__( self, coder: str ):
        message = f"Coder not found in registry: {coder}"
        super( ).__init__( message )


class ConfigurationAbsence( Omnierror, FileNotFoundError ):

    def __init__(
        self, location: __.Absential[ __.Path ] = __.absent
    ) -> None:
        message = "Could not locate agents configuration"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        return (
            f"❌ {self}",
            "",
            "Run 'copier copy gh:emcd/agents-common' to configure agents."
        )


class ConfigurationInvalidity( Omnierror, ValueError ):
    ''' Base configuration data invalidity. '''

    def __init__( self, reason: __.Absential[ str | Exception ] = __.absent ):
        if __.is_absent( reason ): message = "Invalid configuration."
        else: message = f"Invalid configuration: {reason}"
        super( ).__init__( message )



class ContentAbsence( Omnierror, FileNotFoundError ):
    ''' Content file absence. '''

    def __init__( self, content_type: str, content_name: str, coder: str ):
        message = (
            f"No {content_type} content found for {coder}: {content_name}" )
        super( ).__init__( message )


class FileOperationFailure( Omnierror, OSError ):
    ''' File or directory operation failure. '''

    def __init__( self, path: __.Path, operation: str = "access file" ):
        message = f"Failed to {operation}: {path}"
        super( ).__init__( message )


class InstructionSourceInvalidity( Omnierror, ValueError ):
    ''' Instruction source configuration invalidity. '''


class InstructionSourceFieldAbsence( InstructionSourceInvalidity ):
    ''' Instruction source 'source' field absence. '''

    def __init__( self ):
        message = "Instruction source missing required 'source' field."
        super( ).__init__( message )


class InstructionFilesConfigurationInvalidity(
    InstructionSourceInvalidity
):
    ''' Instruction files configuration format invalidity. '''

    def __init__( self ):
        message = "Instruction 'files' configuration must be a mapping."
        super( ).__init__( message )


class ContextInvalidity( Omnierror, TypeError ):
    ''' Invalid execution context. '''

    def __init__( self ):
        message = "Invalid execution context: expected agentsmgr.cli.Globals"
        super( ).__init__( message )


class DataSourceNoSupport( Omnierror, ValueError ):
    ''' Unsupported data source format error. '''

    def __init__( self, source_spec: str ):
        message = f"Unsupported source format: {source_spec}"
        super( ).__init__( message )




class GlobalsPopulationFailure( Omnierror, OSError ):
    ''' Global settings population failure. '''

    def __init__( self, source: __.Path, target: __.Path ):
        message = f"Failed to populate global file from {source} to {target}"
        super( ).__init__( message )



class MemoryFileAbsence( Omnierror, FileNotFoundError ):
    ''' Memory file absence.

        Raised when project memory file (conventions.md) does not exist
        but memory symlinks need to be created.
    '''

    def __init__( self, location: __.Path ) -> None:
        self.location = location
        super( ).__init__( f"Memory file not found: {location}" )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders memory file absence with helpful guidance. '''
        lines = [ "## Error: Memory File Not Found" ]
        lines.append( "" )
        lines.append(
            "The project memory file does not exist at the expected "
            "location:" )
        lines.append( "" )
        lines.append( f"    {self.location}" )
        lines.append( "" )
        lines.append(
            "Memory files provide project-specific conventions and "
            "context to AI coding assistants. Create this file before "
            "running `agentsmgr populate`." )
        lines.append( "" )
        lines.append(
            "**Suggested action**: Create "
            "`.auxiliary/configuration/conventions.md` with "
            "project-specific conventions, or copy from a template "
            "project." )
        return tuple( lines )


class TargetModeNoSupport( Omnierror, ValueError ):
    ''' Targeting mode lack of support. '''

    def __init__( self, coder: str, mode: str, reason: str = '' ):
        self.coder = coder
        self.mode = mode
        self.reason = reason
        message = (
            f"The {coder} coder does not support {mode} targeting mode." )
        if reason: message = f"{message} {reason}"
        super( ).__init__( message )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders targeting mode error with helpful guidance. '''
        lines = [
            "## Error: Unsupported Targeting Mode",
            "",
            f"The **{self.coder}** coder does not support "
            f"**{self.mode}** targeting mode.",
        ]
        if self.reason:
            lines.extend( [ "", self.reason ] )
        return tuple( lines )


class TemplateError( Omnierror, ValueError ):
    ''' Template processing error. '''

    def __init__( self, template_name: str ):
        super( ).__init__( f"Template error: {template_name}" )

    @classmethod
    def for_missing_template(
        cls, coder: str, item_type: str
    ) -> __.typx.Self:
        ''' Creates error for missing template. '''
        return cls( f"no {item_type} template found for {coder}" )

    @classmethod
    def for_extension_parse( cls, template_name: str ) -> __.typx.Self:
        ''' Creates error for extension parsing failure. '''
        return cls( f"cannot determine output extension for {template_name}" )


class ToolSpecificationInvalidity( ConfigurationInvalidity ):
    ''' Tool specification invalidity. '''

    def __init__( self, specification: __.typx.Any ):
        message = f"Unrecognized tool specification: {specification}"
        super( ).__init__( message )


class ToolSpecificationTypeInvalidity( ConfigurationInvalidity ):
    ''' Tool specification type invalidity. '''

    def __init__( self, specification: __.typx.Any ):
        specification_type = type( specification ).__name__
        message = (
            f"Tool specification must be string or dict, got: "
            f"{specification_type}" )
        super( ).__init__( message )
