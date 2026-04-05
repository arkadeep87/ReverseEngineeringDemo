Imports LegacyModernization.QuoteGeneration.Backend.Data
Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Backend.Services
    Public Class QuotePricingService
        Private ReadOnly _quoteRepository As QuoteRepository
        Private ReadOnly _referenceRepository As ReferenceDataRepository

        Public Sub New(quoteRepository As QuoteRepository, referenceRepository As ReferenceDataRepository)
            _quoteRepository = quoteRepository
            _referenceRepository = referenceRepository
        End Sub

        Public Function CalculateQuote(request As QuoteRequest, countryRules As LegacyCountryRuleService) As QuoteResult
            Dim basePremium = _referenceRepository.GetBasePremium(request.PolicyType, request.CoverageAmount)
            Dim riskFactor = _quoteRepository.CalculateRiskFactor(request)
            Dim discountAmount = _quoteRepository.CalculateDiscount(request, basePremium)
            Dim taxAmount = _quoteRepository.CalculateCountryTax(request.CountryCode, request.PolicyType, basePremium)

            Dim premiumAfterCoreRules = (basePremium * riskFactor) - discountAmount + taxAmount
            Dim vbCountryAdjustment = countryRules.ApplyCountryAdjustments(request, premiumAfterCoreRules)
            Dim sqlCountryAdjustment = _quoteRepository.CalculateCountrySpecificAdjustment(request, premiumAfterCoreRules)
            Dim countryAdjustment = If(sqlCountryAdjustment <> 0D, sqlCountryAdjustment, vbCountryAdjustment)

            Return New QuoteResult With {
                .BasePremium = basePremium,
                .RiskFactor = riskFactor,
                .DiscountAmount = discountAmount,
                .TaxAmount = taxAmount,
                .CountryAdjustmentAmount = countryAdjustment,
                .FinalPremium = premiumAfterCoreRules + countryAdjustment
            }
        End Function
    End Class
End Namespace
