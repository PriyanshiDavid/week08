// Continuous traffic so the canary has requests to be judged on.
// Run: k6 run -e BASE_URL=http://<ingress-ip> k6/load.js
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: 10,
  duration: '10m',
  thresholds: { http_req_failed: ['rate<0.01'] },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/courses/`);
  check(res, { 'status is 200': (r) => r.status === 200 });
}
