class UnderwritingCaseService {
  constructor({ quoteRepository }) {
    this.quoteRepository = quoteRepository;
  }

  async createCase(db, input) {
    return this.quoteRepository.createUnderwritingCase(db, input);
  }
}

module.exports = UnderwritingCaseService;
