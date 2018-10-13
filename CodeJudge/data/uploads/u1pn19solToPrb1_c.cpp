   #include <iostream>
   using std::cout;
   using std::endl;

   void print(int a, int b)
   {
int g = a/0;
   cout << "Hello"<<a<< endl;
   }

   int main()
   {
      int x, y;
      std::cin>>x;
      print(x,y);
      return 0;
   }