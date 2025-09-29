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


class Omniexception( BaseException ):
    ''' Base for all exceptions raised by package API. '''
    # TODO: Class and instance attribute concealment and immutability.

    _attribute_visibility_includes_: __.cabc.Collection[ str ] = (
        frozenset( ( '__cause__', '__context__', ) ) )


class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions raised by package API. '''


class ConfigurationAbsence( Omnierror, FileNotFoundError ):
    ''' Configuration file absence. '''

    def __init__( self, target: __.Absential[ __.Path ] = __.absent ):
        if __.is_absent( target ): message = "No agents configuration found."
        else: message = f"No agents configuration found in {target}."
        super( ).__init__( message )


class ConfigurationInvalidity( Omnierror, ValueError ):
    ''' Configuration data invalidity. '''


class ContentAbsence( Omnierror, FileNotFoundError ):
    ''' Content file absence. '''

    def __init__( self, content_type: str, content_name: str, coder: str ):
        message = (
            f"No {content_type} content found for {coder}: {content_name}" )
        super( ).__init__( message )


class TemplateAbsence( Omnierror, FileNotFoundError ):
    ''' Template file absence. '''

    def __init__( self, template_type: str, coder: str ):
        message = f"No template found for {coder} {template_type}"
        super( ).__init__( message )


class UnsupportedCoderError( Omnierror, ValueError ):
    ''' Unsupported coder error. '''

    def __init__( self, coder: str ):
        message = f"Unsupported coder: {coder}"
        super( ).__init__( message )


class UnsupportedSourceError( Omnierror, ValueError ):
    ''' Unsupported data source format error. '''

    def __init__( self, source_spec: str ):
        message = f"Unsupported source format: {source_spec}"
        super( ).__init__( message )
