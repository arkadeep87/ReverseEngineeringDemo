
Public Class QuoteService

    Private adjustmentService As New AdjustmentService()

    Public Function SaveQuote(customerId As String, countryCode As String, policyType As String, coverageAmount As Decimal, basePremium As Decimal) As Integer

        Dim quoteId As Integer
        Dim taxAmount As Decimal
        Dim finalPremium As Decimal

        ' NEW: Fetch tax from country_tax_rules
        taxAmount = adjustmentService.GetCountryTax(countryCode, basePremium)

        finalPremium = basePremium + taxAmount

        quoteId = ExecuteScalar("sp_save_quote_header", New With {
            .customer_id = customerId,
            .country_code = countryCode,
            .policy_type = policyType,
            .coverage_amount = coverageAmount,
            .base_premium = basePremium,
            .final_premium = finalPremium
        })

        ' Persist tax as line item
        ExecuteNonQuery("sp_save_quote_line_item", New With {
            .quote_id = quoteId,
            .charge_code = "TAX",
            .amount = taxAmount,
            .source_table = "country_tax_rules"
        })

        Return quoteId

    End Function

End Class
