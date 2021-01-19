# 🤖After Not After
디스코드 서버의 웹 인증 시스템/가입 승인 시스템을 위한 웹서버+디스코드 봇입니다.

## 🧱구성

1. 서버 입장시 환영인사 + 가입링크 DM전달
2. 링크를 타고 들어가면 Oauth 통해 트위터 계정 인증
3. 트위터 계정 인증후 자기소개 웹페이지 (SweetAlert)
4. 전달받은 ProviderData 와 SweetAlert를 통해 얻은 값을 API서버(extentions.api) 로 POST전달
5. 전달받은 데이터를 FireStore DB에 저장 후 WebSocket으로 봇으로 전달
6. 데이터를 이용해 디스코드 자기소개 채널에 자기소개를 올린후, 유저들의 심사 시작
7. 심사과정은 트위터 계정 스크린샷, 트위터 아이디를 올려준후, :+1: :x: 반응을 통해 심사함
8. 미리 설정해둔 찬성값이 나오면, 자동으로 역할 부여후 가입승인

## ⚙️설정

- 이 프로그램은 DB로 Google Firebase의 Firestore 서비스를 이용합니다
- 또한, 트위터 인증또한 Firebase Auth를 사용합니다.
- 필요한 연동 서비스는 총 `Discord`, `Twitter`, `Google Firebase` 3개 입니다.

### Twitter

[트위터 개발자 센터](https://developer.twitter.com)

- 위의 링크를 타고 들어가, 트위터 어플리케이션을 생성합니다. (API 사용 승인 필요)
- Authentication settings 에서 Oauth 사용을 신청합니다
- Callback urls 에 밑의 Firebase Auth 에서 알려준 URL을 입력합니다.
- API KEYS 에 들어가 모든 api키를 메모해둡니다.
- `src/config.py` 의 `TwitterApiKey` 를 채워넣습니다

### Firebase

[Firebase Console](https://console.firebase.google.com)

- 위의 링크를 타고 들어가, 새 프로젝트를 생성합니다.
- Firebase Auth 를 사용신청한 후, 트위터 API 키를 입력합니다.
- Firebase Firestore DB를 사용신청합니다.
- 프로젝트 설정에 들어가 Admin SDK Cert를 발급받고, `cert/` 폴더 안에 `firebasecert.json` 이라는 이름으로 저장합니다.
- 프로젝트 설정에서 웹 앱 하나를 생성한 이후, 웹 인증키를 발급받고, `src/config.py` 의 `firebase_web_cert` 를 채워넣습니다

### Discord

[디스코드 개발자 센터](https://discord.com/developers/)

- 위의 링크를 타고 들어가 New App 버튼을 눌러 새로운 api어플리케이션을 만듭니다.
- Bot 메뉴에 들어가 봇 계정을 생성한 이후, 이름과 프로필 사진등을 커스터마이징 합니다.
- Bot token을 복사해 `src/config.py` 의 `bot_token` 를 채워넣습니다.

### 기타 설정

- `cert/` 폴더 안에 웹사이트 SSL인증서를 넣어주세요. (`privkey.pem`, `fullchain.pem`)
- `src/config.py` 의 `DISCORD SERVER SETTINGS` 부분은 본인의 디스코드 서버 채널/역할 아이디를 입력해주세요
- `src/config.py` 에 있는 `discord_invite` 에는 서버의 영구 초대링크를 넣어주세요.
- 또한, `SITE SETTINGS` 에 `site_url`은 이 웹서버를 돌리는 도메인을 입력합니다.

## 📝오픈소스 라이센스

이 레포지토리는 `GNU General Public License v3.0` 를 따르고 있습니다. 이 소스코드를 사용하시려면 아래 조건을 지켜야 합니다

- :o:상업적 사용을 허용합니다
- :o:복제, 배포, 수정을 허용합니다.
- :information_source:사용시 이 레포지토리와 같은 라이센스를 적용해야 합니다.
- :information_source:사용시 사용 프로그램의 전체 코드를 공개해야 합니다.
- :information_source:이 소스코드를 사용해 발생한 문제의 대한 책임은 사용자에게 있습니다.
- :information_source:원작자는 이 소스코드를 사용한 프로그램에 대한 보증의 책임이 없습니다.
- :information_source:라이센스 전문과 저작권자에 대한 정보를 이 소스코드를 사용한 프로그램 안에 포함해야 합니다.

