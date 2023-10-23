require 'sinatra'
require 'json'
require 'google/cloud/storage'

set :bind, '0.0.0.0'
set :port, 4567

def storage_client
  Google::Cloud::Storage.new(project_id: ENV['GCP_PROJECT_ID'])
end

def load_forecast(local_path)
  require 'csv'
  rows = []
  CSV.foreach(local_path, headers: true) { |row| rows << row.to_h }
  rows
end

get '/health' do
  content_type :json
  { status: 'ok' }.to_json
end

post '/report' do
  content_type :json
  bucket = ENV['GCS_BUCKET_PROCESSED']
  blob = params['forecast_blob'] || 'processed/forecast.parquet'
  # For simplicity in this minimal example, expect a CSV version too
  csv_blob = params['forecast_csv_blob'] || 'processed/forecast.csv'

  tmp = File.join(Dir.mktmpdir, 'forecast.csv')
  storage_client.bucket(bucket).file(csv_blob).download tmp

  rows = load_forecast(tmp)
  # Simple summary: total forecasted revenue next period and per store
  store_totals = Hash.new(0.0)
  grand_total = 0.0
  rows.each do |r|
    v = r['rev_fcst'].to_f
    store_totals[r['store_id']] += v
    grand_total += v
  end

  summary = {
    grand_total_forecast: grand_total.round(2),
    stores: store_totals.transform_values { |v| v.round(2) }
  }

  # Persist summary back to GCS
  out_blob = params['summary_blob'] || 'reports/summary.json'
  storage_client.bucket(bucket).create_file StringIO.new(summary.to_json), out_blob, content_type: 'application/json'

  { status: 'ok', summary: summary, stored_at: out_blob }.to_json
end


