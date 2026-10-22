import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  // Simulate 10 concurrent users
  vus: 130,
  // Run the test for 30 seconds
  duration: '30s',
  thresholds: {
    // 95% of requests should finish within 2 seconds
    http_req_duration: ['p(95)<2000'],
  },
};

export default function () {
  // Test your local homepage
  const res = http.get('http://127.0.0.1:5000/');
  check(res, { 'status is 200': (r) => r.status === 200 });
  // Wait 1 second between requests (simulates a real user)
  sleep(1);
}