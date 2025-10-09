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


class ConfigurationAbsence( Omnierror, FileNotFoundError ):

    def __init__(
        self, location: __.Absential[ __.Path ] = __.absent
    ) -> None:
        message = "Could not locate agents configuration"
        if not __.is_absent( location ):
            message = f"{message} at '{location}'"
        super( ).__init__( f"{message}." )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        lines = [ "## Error: Agent Configuration Not Found" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Run 'copier copy gh:emcd/agents-common' "
            "to configure agents." )
        return tuple( lines )


class ContextInvalidity( Omnierror, TypeError ):
    ''' Invalid execution context. '''

    def __init__( self ):
        message = "Invalid execution context: expected agentsmgr.cli.Globals"
        super( ).__init__( message )


class ConfigurationInvalidity( Omnierror, ValueError ):
    ''' Configuration data invalidity. '''

    TOML_DECODE_ERROR = "TOML decode error."
    UNRECOGNIZED_TOOL_SPEC = "Unrecognized tool specification."
    TOOL_SPEC_TYPE_ERROR = "Tool specification must be string or dict."
    UNKNOWN_SEMANTIC_TOOL = "Unknown semantic tool name."

    def __init__( self, reason: __.typx.Any = None ):
        if reason is None:
            message = "Invalid configuration."
        else:
            message = f"Invalid configuration: {reason}"
        super( ).__init__( message )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders configuration invalidity with helpful guidance. '''
        lines = [ "## Error: Invalid Agent Configuration" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Check configuration file format and "
            "ensure required fields are present." )
        return tuple( lines )


class ContentAbsence( Omnierror, FileNotFoundError ):
    ''' Content file absence. '''

    def __init__( self, content_type: str, content_name: str, coder: str ):
        message = (
            f"No {content_type} content found for {coder}: {content_name}" )
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


class TemplateAbsence( Omnierror, FileNotFoundError ):
    ''' Template file absence. '''

    def __init__( self, template_type: str, coder: str ):
        message = f"No template found for {coder} {template_type}"
        super( ).__init__( message )


class TemplateExtensionError( Omnierror, ValueError ):
    ''' Template extension determination error. '''

    def __init__( self, template_name: str ):
        message = f"Cannot determine output extension for: {template_name}"
        super( ).__init__( message )


class CoderAbsence( Omnierror, ValueError ):
    ''' Coder absence in registry. '''

    def __init__( self, coder: str ):
        message = f"Coder not found in registry: {coder}"
        super( ).__init__( message )


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


class UnsupportedSourceError( Omnierror, ValueError ):
    ''' Unsupported data source format error. '''

    def __init__( self, source_spec: str ):
        message = f"Unsupported source format: {source_spec}"
        super( ).__init__( message )


class DirectoryCreateFailure( Omnierror, OSError ):
    ''' Directory create failure. '''

    def __init__( self, directory: __.Path ):
        message = f"Failed to create directory: {directory}"
        super( ).__init__( message )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders directory creation failure with helpful guidance. '''
        lines = [ "## Error: Directory Creation Failed" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Check directory permissions and available "
            "disk space." )
        return tuple( lines )


class ContentUpdateFailure( Omnierror, OSError ):
    ''' Content file update failure. '''

    def __init__( self, file_path: __.Path ):
        message = f"Failed to update content at: {file_path}"
        super( ).__init__( message )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders content update failure with helpful guidance. '''
        lines = [ "## Error: Content Update Failed" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Check file permissions and ensure parent "
            "directory exists." )
        return tuple( lines )


class GlobalsPopulationFailure( Omnierror, OSError ):
    ''' Global settings population failure. '''

    def __init__( self, source: __.Path, target: __.Path ):
        message = f"Failed to populate global file from {source} to {target}"
        super( ).__init__( message )

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders globals population failure with helpful guidance. '''
        lines = [ "## Error: Globals Population Failed" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Check file permissions and ensure source "
            "file is valid." )
        return tuple( lines )


class ContentGenerationFailure( Omnierror, RuntimeError ):
    ''' Content generation failure. '''
