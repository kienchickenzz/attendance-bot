import traceback

class InternalError( Exception ):
    def __init__( self, status_code: int, message: str ):
        self.status_code = status_code
        self.message = message
        super().__init__( self.message )

        self.stack_trace = self._capture_stack_trace()

    def _capture_stack_trace( self ):
        stack = traceback.extract_stack()
        
        # Remove last frame (_capture_stack_trace) and __init__ frame
        relevant_stack = stack[ :-2 ]
        
        formatted_stack = []
        for frame in relevant_stack:
            formatted_stack.append(
                f'  File "{ frame.filename }", line { frame.lineno }, in { frame.name }\n'
                f'    { frame.line }'
            )
        
        return '\n'.join( formatted_stack )
