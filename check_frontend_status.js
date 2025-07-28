const http = require('http');

console.log('프론트엔드 서버 상태 확인 중...\n');

// localhost:3000 확인
const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/',
  method: 'GET',
  timeout: 5000
};

const req = http.request(options, (res) => {
  console.log(`상태 코드: ${res.statusCode}`);
  console.log(`헤더:`, res.headers);
  
  if (res.statusCode === 200) {
    console.log('\n✅ 프론트엔드 서버가 정상적으로 실행 중입니다!');
    console.log('브라우저에서 http://localhost:3000 으로 접속하세요.');
  } else {
    console.log('\n⚠️ 서버는 실행 중이지만 응답이 예상과 다릅니다.');
  }
  
  res.on('data', (chunk) => {
    console.log('\n응답 본문 (첫 200자):');
    console.log(chunk.toString().substring(0, 200) + '...');
  });
});

req.on('error', (err) => {
  console.error('\n❌ 연결 실패:', err.message);
  console.log('\n가능한 원인:');
  console.log('1. 프론트엔드 서버가 아직 시작 중입니다 (1-2분 소요)');
  console.log('2. 포트 3000이 다른 프로그램에 의해 사용 중입니다');
  console.log('3. 방화벽이 연결을 차단하고 있습니다');
  console.log('\n해결 방법:');
  console.log('1. start_frontend.bat 실행');
  console.log('2. 잠시 기다린 후 다시 시도');
});

req.on('timeout', () => {
  console.error('\n❌ 연결 시간 초과');
  req.destroy();
});

req.end();