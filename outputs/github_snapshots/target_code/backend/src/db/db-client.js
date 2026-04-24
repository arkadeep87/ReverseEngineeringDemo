class DbClient {
  async query(sql, params = []) {
    return { rows: [], sql, params };
  }
}

const dbClient = new DbClient();

module.exports = { dbClient };
