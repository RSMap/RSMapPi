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


        // Store strategy defines how many entries are needed to send
        // due to real time requirements is set to 1.
        kaaClient.setLogUploadStrategy(new RecordCountLogUploadStrategy(1));
        kaaClient.start();
        System.out.println("Waiting for KAA client");

        // Wait 30 sec before starting read data
        try{
            TimeUnit.SECONDS.sleep(30L);
        } catch (InterruptedException e) {
            System.out.println("e.GetMessage()");
        }

        String fromclient;

        // Socket Initializing, it will receive data from VehicleAnalyzer.py
        try{
        System.out.println("Initializing local socket...");
        ServerSocket Server = new ServerSocket (5000);

        System.out.println ("Waint for VehicleAnalyzer on TCP socket at port 5000");

        // Listening connections
        Socket connected = Server.accept();
        System.out.println( " VehicleAnalyzer with "+ connected.getInetAddress() +":"+connected.getPort()+" is connected! ");

        // Init reading buffer over TCP socket
        BufferedReader inFromClient = new BufferedReader(new InputStreamReader (connected.getInputStream()));

        // First two packets comes with device location and device id
        String location = inFromClient.readLine();
        String device = inFromClient.readLine();

        System.out.println("Device from: " + location);
        System.out.println("Device id: " + device);

        while ( true ){
            // read lines from socket
            fromclient = inFromClient.readLine();

            // stop signal
            if ( fromclient.equals("q") || fromclient.equals("Q") ){
                connected.close();
                break;
            }else {
              // create new AudioReport object wich is appended to Cassandra
              AudioReport report = new AudioReport();
              long timestamp = System.currentTimeMillis();
              report.setZoneId(location);
              report.setDeviceId(device);
              report.setLevel(Double.parseDouble(fromclient));
              report.setTimestamp(timestamp);

              // send Audio Report object
              kaaClient.addLogRecord(report);

              // wait 1 MILLISECONDS to avoid overwrite data with the same ts
              try{
                  TimeUnit.MILLISECONDS.sleep(1L);
              } catch (InterruptedException e) {
                  System.out.println("e.GetMessage()");
              }

            }
        }
      }catch (IOException e){
        System.out.println("Socket error");
      }

      System.out.println("VehicleAnalyzer is now stopped, exiting.");

      // release all resources in use
      kaaClient.stop();

      // wait for resource release
      try{
          TimeUnit.SECONDS.sleep(60L);
      } catch (InterruptedException e) {
          System.out.println("e.GetMessage()");
      }
    }
}
