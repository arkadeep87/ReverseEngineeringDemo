Imports LegacyModernization.QuoteGeneration.Backend.Data
Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Backend.Services
    Public Class QuotePersistenceService
        Private ReadOnly _quoteRepository As QuoteRepository
        Private ReadOnly _auditRepository As AuditRepository

        Public Sub New(quoteRepository As QuoteRepository, auditRepository As AuditRepository)
            _quoteRepository = quoteRepository
            _auditRepository = auditRepository
        End Sub

        Public Sub PersistQuote(request As QuoteRequest, result As QuoteResult, countryNote As String)
            Dim quoteId = _quoteRepository.SaveQuoteHeader(request, result)
            result.QuoteId = quoteId

            _quoteRepository.SaveQuoteContext(quoteId, request, result)
            _quoteRepository.SaveQuoteLineItem(quoteId, "BASE_PREMIUM", result.BasePremium, "quote_line_item")
            _quoteRepository.SaveQuoteLineItem(quoteId, "COUNTRY_ADJUSTMENT", result.CountryAdjustmentAmount, "quote_line_item")
            _quoteRepository.SaveUnderwritingCase(quoteId, request.CustomerId, request.CountryCode)
            _auditRepository.LogQuoteEvent(quoteId, "QUOTE_GENERATED", countryNote)
        End Sub
    End Class
End Namespace
