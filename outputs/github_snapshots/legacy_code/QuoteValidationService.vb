Imports LegacyModernization.QuoteGeneration.Backend.Data
Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Backend.Services
    Public Class QuoteValidationService
        Private ReadOnly _quoteRepository As QuoteRepository
        Private ReadOnly _referenceRepository As ReferenceDataRepository

        Public Sub New(quoteRepository As QuoteRepository, referenceRepository As ReferenceDataRepository)
            _quoteRepository = quoteRepository
            _referenceRepository = referenceRepository
        End Sub

        Public Sub ValidateRequest(request As QuoteRequest)
            Dim customer = _quoteRepository.GetCustomerProfile(request.CustomerId)
            Dim policy = _referenceRepository.GetPolicyCatalog(request.PolicyType)
            Dim schedule = _referenceRepository.GetPaymentSchedule(request.PaymentFrequency)
            Dim transientQuoteId = _quoteRepository.EnsureQuoteContextDraft(request)

            If customer Is Nothing Then
                Throw New ApplicationException("Customer profile not found in customer_profile table.")
            End If

            If policy Is Nothing OrElse schedule Is Nothing Then
                Throw New ApplicationException("Policy or payment schedule reference data is incomplete.")
            End If

            _quoteRepository.EnsureEligibility(request)

            If request.GdprConsentGranted Then
                _quoteRepository.UpsertConsent(request.CustomerId, transientQuoteId, request.CountryCode, "GDPR")
            Else
                _quoteRepository.RunGdprAudit()
            End If

            _quoteRepository.ValidateGdprConsent(transientQuoteId, request.CountryCode)
        End Sub
    End Class
End Namespace
