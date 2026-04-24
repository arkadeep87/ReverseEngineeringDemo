const SupportedCountryValidator = require('../../src/services/supportedCountryValidator');

describe('SupportedCountryValidator', () => {
  test('accepts approved countries', () => {
    const validator = new SupportedCountryValidator();
    expect(() => validator.validate('ES')).not.toThrow();
    expect(() => validator.validate('DE')).not.toThrow();
    expect(() => validator.validate('IT')).not.toThrow();
    expect(() => validator.validate('PT')).not.toThrow();
    expect(() => validator.validate('CH')).not.toThrow();
    expect(() => validator.validate('GB')).not.toThrow();
  });

  test('rejects unsupported countries with business-readable message', () => {
    const validator = new SupportedCountryValidator();
    expect(() => validator.validate('FR')).toThrow('The selected country is outside the approved quote scope.');
  });
});
