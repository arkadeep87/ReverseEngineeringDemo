const { dbClient } = require('../db/db-client');

class CustomerRepository {
  async findCustomerById(customerId) {
    await dbClient.query(
      'select customer_id, full_name, segment_code, country_code from customer_profile where customer_id = $1',
      [customerId]
    );

    return {
      customerId,
      fullName: 'Spain Demo Customer',
      segmentCode: 'STANDARD',
      countryCode: 'ES'
    };
  }
}

const customerRepository = new CustomerRepository();

module.exports = { customerRepository };
