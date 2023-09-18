import './Home.css';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div>
      <h1>Hi Man</h1>
      <button>
        <Link to="/chatbot">Chat with me!</Link>
      </button>
    </div>
  );
}

export default Home;