Namespace LegacyModernization.QuoteGeneration.Forms
    Public Class PortugalQuoteGenerationForm
        Inherits BaseQuoteGenerationForm

        Protected Overrides ReadOnly Property CountryCode As String = "PT"
        Protected Overrides ReadOnly Property CountryDisplayName As String = "Portugal"

        Protected Overrides Sub ConfigureCountryDefaults()
            MyBase.ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "FAMILY"
            lblCountryHint.Text = "Portugal quotes account for solidarity levy and annual-payment benefits."
        End Sub
    End Class
End Namespace
