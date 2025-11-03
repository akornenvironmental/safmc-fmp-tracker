const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="text-center text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} SAFMC FMP Tracker. Data sourced from{' '}
            <a
              href="https://safmc.net"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-blue hover:text-brand-green transition-colors"
            >
              SAFMC.net
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
