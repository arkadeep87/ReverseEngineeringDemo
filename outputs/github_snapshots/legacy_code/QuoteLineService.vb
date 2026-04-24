
Public Class QuoteLineService

    Public Sub AddLineItem(quoteId As Integer, chargeCode As String, amount As Decimal, source As String)

        ExecuteNonQuery("sp_save_quote_line_item", New With {
            .quote_id = quoteId,
            .charge_code = chargeCode,
            .amount = amount,
            .source_table = source
        })

    End Sub

End Class
