use anyhow::Result;
use elasticsearch::{Elasticsearch, indices::{IndicesCreateParts, IndicesExistsParts}, http::transport::Transport,};
use serde_json::json;

#[tokio::main]
async fn main() -> Result<()> {
    println!("Connecting to Elasticsearch...");
    
    let transport = Transport::single_node("http://localhost:9200")?;
    let client = Elasticsearch::new(transport);
    
    // Define the index name
    let index_name = "my_index";
    
    // Check if the index already exists
    let exists_response = client
        .indices()
        .exists(IndicesExistsParts::Index(&[index_name]))
        .send()
        .await?;
    
    if exists_response.status_code() == 200 {
        println!("Index '{}' already exists", index_name);
    } else {
        // Create the index with mappings
        println!("Creating index '{}'...", index_name);
        
        let response = client
            .indices()
            .create(IndicesCreateParts::Index(index_name))
            .body(json!({
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "title": { "type": "text" },
                        "content": { "type": "text" },
                        "date": { "type": "date" },
                        "tags": { "type": "keyword" }
                    }
                }
            }))
            .send()
            .await?;
        
        if response.status_code().is_success() {
            println!("Successfully created index '{}'", index_name);
        } else {
            println!("Failed to create index: {:?}", response.text().await?);
        }
    }
    
    Ok(())
}
