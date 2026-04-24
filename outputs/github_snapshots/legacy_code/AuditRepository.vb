Imports System.Collections.Generic

Namespace LegacyModernization.QuoteGeneration.Backend.Data
    Public Class AuditRepository
        Private ReadOnly _db As New LegacyDbContext()

        Public Sub LogQuoteEvent(quoteId As Integer, eventType As String, eventMessage As String)
            Dim sql = "INSERT INTO audit_event (quote_id, event_type, event_message, created_at) " &
                      "VALUES (@quote_id, @event_type, @event_message, GETDATE())"
            _db.ExecuteScalarQuery(
                sql,
                New Dictionary(Of String, Object) From {
                    {"@quote_id", quoteId},
                    {"@event_type", eventType},
                    {"@event_message", eventMessage}
                }
            )
        End Sub
    End Class
End Namespace
