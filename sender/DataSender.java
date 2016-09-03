import org.kaaproject.kaa.client.DesktopKaaPlatformContext;
import org.kaaproject.kaa.client.Kaa;
import org.kaaproject.kaa.client.KaaClient;
import org.kaaproject.kaa.client.KaaClientPlatformContext;
import org.kaaproject.kaa.client.SimpleKaaClientStateListener;
import org.kaaproject.kaa.client.logging.strategies.RecordCountLogUploadStrategy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.kaaproject.kaa.schema.rsmap.AudioReport;

import java.net.Socket;
import java.net.ServerSocket;

import java.io.*;
import java.util.concurrent.TimeUnit;
import java.io.IOException;

public class DataSender {

    public static void main(String[] args) {

        KaaClientPlatformContext context = new DesktopKaaPlatformContext();
        KaaClient kaaClient = Kaa.newClient(context, new SimpleKaaClientStateListener() {
            @Override
            public void onStarted() {
                System.out.println("KAA client started!");
            }

            @Override
            public void onStopped() {
                System.out.println("Kaa client stopped!");
            }
        });

        // Set a custom strategy for uploading logs.
        // The default strategy uploads logs after either a threshold logs count
        // or a threshold logs size has been reached.
        // The following custom strategy uploads every log record as soon as it
        // is created.
        kaaClient.setLogUploadStrategy(new RecordCountLogUploadStrategy(1));
        kaaClient.start();
        System.out.println("Waiting for KAA client");

        try{
            TimeUnit.SECONDS.sleep(30L);
        } catch (InterruptedException e) {
            System.out.println("e.GetMessage()");
        }

        String fromclient;

        try{
        System.out.println("Initializing local socket...");
        ServerSocket Server = new ServerSocket (5000);

        System.out.println ("TCPServer Waiting for client on port 5000");

        Socket connected = Server.accept();
        System.out.println( " THE CLIENT"+" "+ connected.getInetAddress() +":"+connected.getPort()+" IS CONNECTED ");

        BufferedReader inFromClient = new BufferedReader(new InputStreamReader (connected.getInputStream()));

        String location = inFromClient.readLine();
        String device = inFromClient.readLine();

        System.out.println("Device from: " + location);
        System.out.println("Device id: " + device);

        while ( true ){
            fromclient = inFromClient.readLine();

            if ( fromclient.equals("q") || fromclient.equals("Q") ){
                connected.close();
                break;
            }else {
              AudioReport report = new AudioReport();
              long timestamp = System.currentTimeMillis();
              report.setZoneId(location);
              report.setDeviceId(device);
              report.setLevel(Double.parseDouble(fromclient));
              report.setTimestamp(timestamp);
              kaaClient.addLogRecord(report);

              try{
                  TimeUnit.MILLISECONDS.sleep(1L);
              } catch (InterruptedException e) {
                  System.out.println("e.GetMessage()");
              }

            }
        }
      }catch (IOException e){
        System.out.println("err");
      }

      System.out.println("Saliendo!");

        // try {
    		// 	BufferedReader bufferRead = new BufferedReader(new InputStreamReader(System.in));
    		// 	//PrintWriter writer = new PrintWriter("result.txt", "UTF-8");
    		// 	boolean cont = true;
    		// 	while(cont) {
    		// 		//writer.println(s);
    		// 		String s = bufferRead.readLine();
    		// 		if(!s.equals("x")){
    		// 			//writer.close();
        //       AudioReport report = new AudioReport();
        //       long timestamp = System.currentTimeMillis();
        //       report.setZoneId("Granada");
        //       report.setDeviceId("Device 1");
        //       report.setLevel(Double.parseDouble(s));
        //       report.setTimestamp(timestamp);
        //       // logs.add(report);
        //
        //       kaaClient.addLogRecord(report);
    		// 		}else{
        //       cont = false;
        //     }
    		// 	}
        //   System.out.println("saliendo!");
        //
        //
    		// } catch(IOException e) {
    		// 	e.printStackTrace();
    		// }
        //
        // System.out.println("sigo saliendo!");
        // // create audio report
        // // AudioReport report = new AudioReport();
        // // long timestamp = System.currentTimeMillis();
        // // report.setZoneId("Granada");
        // // report.setDeviceId("Device 1");
        // // report.setLevel(0.93);
        // // report.setTimestamp(timestamp);
        // // // logs.add(report);
        // //
        // // kaaClient.addLogRecord(report);
        //
        //
        // // Stop the Kaa client and release all the resources which were in use.
        try{
            TimeUnit.SECONDS.sleep(60L);
        } catch (InterruptedException e) {
            System.out.println("e.GetMessage()");
        }
        kaaClient.stop();
        //LOG.info("Zeppelin data analytics demo stopped");
    }
}
