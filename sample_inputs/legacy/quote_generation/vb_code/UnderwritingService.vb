
Public Class UnderwritingService

    Public Sub CreateUnderwritingCase(quoteId As Integer, customerId As String, countryCode As String)

        ExecuteNonQuery("sp_save_underwriting_case", New With {
            .quote_id = quoteId,
            .customer_id = customerId,
            .country_code = countryCode
        })

    End Sub

End Class
