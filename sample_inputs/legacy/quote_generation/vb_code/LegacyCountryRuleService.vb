Imports LegacyModernization.QuoteGeneration.Backend.Models

Namespace LegacyModernization.QuoteGeneration.Backend.Services
    Public Class LegacyCountryRuleService
        Public Function ApplyCountryAdjustments(request As QuoteRequest, currentPremium As Decimal) As Decimal
            Select Case request.CountryCode
                Case "DE"
                    Dim insuranceDuty = currentPremium * 0.032D
                    Dim socialHealthSurcharge = If(request.PolicyType = "HEALTH", currentPremium * 0.014D, 0D)
                    Return insuranceDuty + socialHealthSurcharge
                Case "IT"
                    Dim stampDuty = 22D
                    Dim familyRelief = If(request.PolicyType = "FAMILY", -12D, 0D)
                    Return stampDuty + familyRelief
                Case "ES"
                    Dim consortiumLevy = currentPremium * 0.018D
                    Dim travelAssistReserve = If(request.PolicyType = "TRAVEL", 9.5D, 0D)
                    Return consortiumLevy + travelAssistReserve
                Case "PT"
                    Dim solidarityLevy = currentPremium * 0.012D
                    Dim annualCollectionRelief = If(request.PaymentFrequency = "ANNUAL", -7.5D, 0D)
                    Return solidarityLevy + annualCollectionRelief
                Case "CH"
                    Dim cantonalReserve = currentPremium * 0.021D
                    Dim corporateHandlingFee = If(request.PolicyType = "CORPORATE", 35D, 0D)
                    Return cantonalReserve + corporateHandlingFee
                Case "GB"
                    Dim insurancePremiumTax = currentPremium * 0.12D
                    Dim travelSecurityFee = If(request.PolicyType = "TRAVEL", 6D, 0D)
                    Return insurancePremiumTax + travelSecurityFee
                Case Else
                    Throw New ApplicationException("Unsupported country code for legacy quote generation.")
            End Select
        End Function

        Public Function BuildCountryNote(request As QuoteRequest) As String
            Select Case request.CountryCode
                Case "DE"
                    Return "Germany processing applied DE insurance duty and statutory health surcharge."
                Case "IT"
                    Return "Italy processing applied stamp duty and optional family relief."
                Case "ES"
                    Return "Spain processing applied consortium levy and travel assistance reserve."
                Case "PT"
                    Return "Portugal processing applied solidarity levy and annual collection relief."
                Case "CH"
                    Return "Switzerland processing applied cantonal reserve loading and corporate handling fee."
                Case "GB"
                    Return "United Kingdom processing applied insurance premium tax and travel security fee."
                Case Else
                    Throw New ApplicationException("Unsupported country code for legacy quote generation.")
            End Select
        End Function
    End Class
End Namespace
