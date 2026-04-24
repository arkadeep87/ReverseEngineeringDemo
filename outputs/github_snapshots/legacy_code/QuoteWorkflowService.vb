Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Backend.Services
    Public Class QuoteWorkflowService
        Public Function GenerateQuote(request As QuoteRequest) As QuoteResult
            Dim countryRules As New LegacyCountryRuleService()
            Dim processor As New CommonCountryQuoteProcessor(countryRules)
            Return processor.ProcessQuote(request)
        End Function
    End Class
End Namespace
