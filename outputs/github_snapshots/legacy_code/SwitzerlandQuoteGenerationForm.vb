Namespace LegacyModernization.QuoteGeneration.Forms
    Public Class SwitzerlandQuoteGenerationForm
        Inherits BaseQuoteGenerationForm

        Protected Overrides ReadOnly Property CountryCode As String = "CH"
        Protected Overrides ReadOnly Property CountryDisplayName As String = "Switzerland"

        Protected Overrides Sub ConfigureCountryDefaults()
            MyBase.ConfigureCountryDefaults()
            cboPolicyType.SelectedItem = "CORPORATE"
            lblCountryHint.Text = "Switzerland quotes apply cantonal reserve loading and non-EU privacy handling."
        End Sub
    End Class
End Namespace
