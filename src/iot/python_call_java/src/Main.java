import java.io.*;



public class Main{



    public static void main(String[] args) {

        Me m = new Me(3);

        try {
            System.out.println("Waiting...");
            BufferedReader bufferRead = new BufferedReader(new InputStreamReader(System.in));
            PrintWriter writer = new PrintWriter("result.txt", "UTF-8");
            String s = bufferRead.readLine();

            while(s.equals("x")==false) {
                writer.println(s);
                s = bufferRead.readLine();
            }
            writer.close();
            System.out.println("Conexion ended...");
        } catch(IOException e) {
            e.printStackTrace();
        }
    }
}
