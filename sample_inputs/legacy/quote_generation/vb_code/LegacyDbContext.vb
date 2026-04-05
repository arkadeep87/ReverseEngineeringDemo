Imports System.Collections.Generic

Namespace LegacyModernization.QuoteGeneration.Backend.Data
    Public Class LegacyDbContext
        Public Function ExecuteStoredProcedure(name As String, parameters As Dictionary(Of String, Object)) As Dictionary(Of String, Object)
            Return New Dictionary(Of String, Object)()
        End Function

        Public Function ExecuteScalarQuery(sql As String, parameters As Dictionary(Of String, Object)) As Object
            Return Nothing
        End Function
    End Class
End Namespace
