# CLI Output Formatting and Error Handling Strategy

## Executive Summary

This document outlines the enhancement strategy for `agentsmgr` CLI output formatting, adopting patterns from librovore's sophisticated result and exception rendering system. The approach emphasizes result objects with Markdown rendering and standardized error interception.

## Current State Analysis

**Existing Approach (DetectCommand):**
```python
# Direct printing in command implementation
print( "🔍 Agent Configuration Detected:" )
print( f"   Coders: {', '.join( configuration[ 'coders' ] )}" )
```

**Limitations:**
- Hard to test (print statements vs. assertable data structures)
- Inconsistent formatting across commands
- No programmatic access to results
- Error handling mixed with display logic

## Proposed Enhancement Strategy

### Result Objects with Markdown Rendering

**Base Protocol:**
```python
class ResultBase( __.abc.ABC ):
    ''' Base protocol for command result objects with rendering. '''

    @__.abc.abstractmethod
    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders result as Markdown lines for display. '''
        raise NotImplementedError
```

**Configuration Detection Result:**
```python
class ConfigurationDetectionResult( ResultBase ):
    ''' Agent configuration detection result with formatting. '''

    target: __.Path
    coders: tuple[ str, ... ]
    languages: tuple[ str, ... ]
    project_name: __.typx.Optional[ str ] = None

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        lines = [ "🔍 Agent Configuration Detected:" ]
        lines.append( f"   Coders: {', '.join( self.coders )}" )
        lines.append( f"   Languages: {', '.join( self.languages )}" )
        if self.project_name:
            lines.append( f"   Project: {self.project_name}" )
        lines.append( f"   Target Directory: {self.target.resolve( )}" )
        return tuple( lines )
```

### Enhanced Exception Rendering

**Base Exception Enhancement:**
```python
class Omnierror( Omniexception, Exception ):
    ''' Base for error exceptions with rendering capability. '''

    @__.abc.abstractmethod
    def render_as_markdown( self ) -> tuple[ str, ... ]:
        ''' Renders exception as Markdown lines for display. '''
        raise NotImplementedError
```

**Configuration Error Examples:**
```python
class ConfigurationAbsence( Omnierror, FileNotFoundError ):
    ''' Configuration file absence with helpful guidance. '''

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        lines = [ "## Error: Agent Configuration Not Found" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Run 'copier copy gh:emcd/agents-common' "
            "to configure agents." )
        return tuple( lines )

class ConfigurationInvalidity( Omnierror, ValueError ):
    ''' Configuration data invalidity with specific guidance. '''

    def render_as_markdown( self ) -> tuple[ str, ... ]:
        lines = [ "## Error: Invalid Agent Configuration" ]
        lines.append( f"**Message:** {self}" )
        lines.append(
            "**Suggestion:** Check configuration file format and "
            "ensure required fields are present." )
        return tuple( lines )
```

### Error Interception Decorator

**Adapted from librovore's `intercept_errors` pattern:**
```python
def intercept_errors(
    exit_code: int = 1,
) -> __.cabc.Callable[
    [ __.cabc.Callable[ [ ], __.cabc.Awaitable[ __.typx.Any ] ] ],
    __.cabc.Callable[ [ ], __.cabc.Awaitable[ None ] ]
]:
    ''' Decorator to intercept and render exceptions with proper exit codes. '''

    def decorator(
        function: __.cabc.Callable[ [ ], __.cabc.Awaitable[ __.typx.Any ] ]
    ) -> __.cabc.Callable[ [ ], __.cabc.Awaitable[ None ] ]:
        @__.wraps( function )
        async def wrapper( ) -> None:
            try:
                result = await function( )
                if hasattr( result, 'render_as_markdown' ):
                    lines = result.render_as_markdown( )
                    for line in lines:
                        print( line )
                elif result is not None:
                    print( result )
            except _exceptions.Omnierror as exception:
                if hasattr( exception, 'render_as_markdown' ):
                    lines = exception.render_as_markdown( )
                    for line in lines:
                        print( line, file = __.sys.stderr )
                else:
                    print( f"❌ {exception}", file = __.sys.stderr )
                raise SystemExit( exit_code ) from None
        return wrapper
    return decorator
```

### Command Integration Pattern

**Simplified Command Implementation:**
```python
class DetectCommand( __.appcore_cli.Command ):
    target: __.Path = __.dcls.field( default_factory = __.Path.cwd )

    @intercept_errors( exit_code = 1 )
    async def execute( self, auxdata: __.appcore_state.Globals ) -> ConfigurationDetectionResult:
        ''' Detects agent configuration and returns structured result. '''
        configuration = await self._detect_configuration( self.target )
        return ConfigurationDetectionResult(
            target = self.target,
            coders = tuple( configuration[ 'coders' ] ),
            languages = tuple( configuration[ 'languages' ] ),
            project_name = configuration.get( 'project_name' ),
        )

    async def _detect_configuration( self, target: __.Path ) -> __.cabc.Mapping[ str, __.typx.Any ]:
        ''' Loads and validates configuration - raises exceptions on failure. '''
        # Configuration detection logic (unchanged)
        # Exceptions automatically caught and rendered by decorator
```

## Implementation Benefits

### Development Experience
- **Testable Results**: Assert on result objects instead of captured output
- **Consistent Formatting**: All commands follow same rendering patterns
- **Separation of Concerns**: Logic vs. presentation cleanly separated
- **Error Standardization**: Uniform error handling across commands

### User Experience
- **Professional Output**: Consistent, well-formatted command output
- **Helpful Error Messages**: Structured errors with actionable suggestions
- **Predictable Interface**: Same output patterns across all commands

### Future Extensibility
- **Easy Format Addition**: JSON, TOML, XML rendering can be added later
- **Rich Display Integration**: Natural fit with appcore's display options
- **Complex Results**: Scales to PopulateCommand's multi-file results
- **Error Aggregation**: Multiple errors can be collected and displayed together

## Migration Strategy

### Phase 1: Foundation (Immediate)
- Create `ResultBase` protocol and basic result objects
- Implement `intercept_errors` decorator
- Enhance exception classes with `render_as_markdown()`

### Phase 2: Command Migration
- Migrate `DetectCommand` to result-based approach
- Validate pattern with existing functionality
- Establish testing patterns for result objects

### Phase 3: Expansion
- Apply pattern to `PopulateCommand` and `ValidateCommand`
- Add complex result aggregation for multi-operation commands
- Consider additional output formats (JSON) if needed

This approach transforms `agentsmgr` from basic print-based output to a professional, extensible CLI with consistent, testable, and user-friendly interfaces following proven patterns from the librovore ecosystem.