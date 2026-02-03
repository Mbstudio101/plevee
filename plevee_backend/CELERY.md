# Celery Worker Setup

## Starting the Celery Worker

### Development
```bash
cd plevee_backend
celery -A app.celery_app worker --loglevel=info -Q strategies,market_data
```

### With Beat Scheduler (for periodic tasks)
```bash
celery -A app.celery_app worker --beat --loglevel=info
```

### Production (with multiple workers)
```bash
# Strategy execution worker
celery -A app.celery_app worker --loglevel=info -Q strategies -n strategy_worker@%h

# Market data worker  
celery -A app.celery_app worker --loglevel=info -Q market_data -n market_data_worker@%h

# Beat scheduler (only one instance needed)
celery -A app.celery_app beat --loglevel=info
```

## Monitoring

### Flower (Web-based monitoring)
```bash
pip install flower
celery -A app.celery_app flower
```
Then visit: http://localhost:5555

### Check task status
```python
from app.tasks.strategy_executor import execute_strategy

# Start task
result = execute_strategy.delay("strategy-uuid-here")

# Check status
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Task result
```

## Task Queues

- **strategies**: Strategy execution tasks
- **market_data**: Market data updates and fetching

## Periodic Tasks

- **update-market-data**: Runs every 60 seconds to update prices

## Configuration

Celery is configured to use Redis as both broker and result backend.
Make sure Redis is running before starting workers.
