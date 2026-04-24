Imports LegacyModernization.QuoteGeneration.Backend.Models
Imports LegacyModernization.QuoteGeneration.Backend.Services

Namespace LegacyModernization.QuoteGeneration.Backend.Facade
    Public Class QuoteSubmissionFacade
        Private ReadOnly _workflow As New QuoteWorkflowService()

        Public Function SubmitQuote(request As QuoteRequest) As QuoteResult
            Return _workflow.GenerateQuote(request)
        End Function
    End Class
End Namespace
