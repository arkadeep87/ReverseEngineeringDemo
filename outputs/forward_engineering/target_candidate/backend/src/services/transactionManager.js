class TransactionManager {
  constructor({ pool }) {
    this.pool = pool;
  }

  async runInTransaction(work, onError) {
    const client = await this.pool.connect();
    try {
      await client.query('BEGIN');
      const result = await work(client);
      await client.query('COMMIT');
      return result;
    } catch (error) {
      await client.query('ROLLBACK');
      if (onError) {
        try {
          await onError(error, client);
        } catch (ignored) {}
      }
      throw error;
    } finally {
      client.release();
    }
  }
}

module.exports = TransactionManager;
