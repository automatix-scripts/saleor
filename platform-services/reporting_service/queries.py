# /home/ubuntu/platform-services/reporting_service/queries.py
# Autor: Szymon Fuchs
# Data: 06.09.2021

ORDERS_QUERY = """
query GetOrders(
  $channel: String,
  $createdGte: DateTime,
  $createdLte: DateTime,
  $first: Int,
  $after: String
) {
  orders(
    first: $first,
    after: $after,
    filter: {
      channel: $channel,
      created: { gte: $createdGte, lte: $createdLte }
    }
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        number
        created
        status
        total {
          gross {
            amount
            currency
          }
        }
        lines {
          id
          productName
          variantName
          quantity
          unitPrice {
            gross { amount currency }
          }
          totalPrice {
            gross { amount currency }
          }
        }
      }
    }
  }
}
"""

PRODUCT_PERFORMANCE_QUERY = """
query GetProductPerformance(
  $channel: String,
  $createdGte: DateTime,
  $createdLte: DateTime,
  $first: Int,
  $after: String
) {
  orders(
    first: $first,
    after: $after,
    filter: {
      channel: $channel,
      created: { gte: $createdGte, lte: $createdLte }
    }
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        lines {
          productSku
          productName
          variantName
          quantity
          totalPrice {
            gross {
              amount
            }
          }
        }
      }
    }
  }
}
"""
